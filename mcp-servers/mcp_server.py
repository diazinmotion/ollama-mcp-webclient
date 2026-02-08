from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import datetime
import uvicorn
import httpx
import mlflow
from db_config import get_config, get_db_tools, get_all_configs

# Initialize MLflow tracking
MLFLOW_TRACKING_URI = "http://localhost:5001"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("LLM Interactions")

app = FastAPI()

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/log/chat")
async def log_chat_interaction(request: Request):
    try:
        data = await request.json()
        user_input = data.get("input", "")
        ai_output = data.get("output", "")
        session_id = data.get("sessionId", "unknown")
        model_name = data.get("model", "unknown")
        
        with mlflow.start_run(run_name=f"Chat_{session_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_param("sessionId", session_id)
            mlflow.log_param("model", model_name)
            mlflow.log_text(user_input, "user_input.txt")
            mlflow.log_text(ai_output, "ai_output.txt")
            mlflow.set_tag("type", "llm_interaction")
            
        return {"status": "success", "message": "Interaction logged to MLflow"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/")
async def mcp_endpoint(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params", {})
    rpc_id = data.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": get_db_tools(),
                "name": "TimeWeatherServer",
                "configs": get_all_configs()
            }
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "get_current_time":
            now = datetime.datetime.now()
            result = f"The current local date and time is: {now.strftime('%A, %B %d, %Y %H:%M:%S')}"
        elif tool_name == "get_ip":
          try:
            url = get_config("ip_api_url")
            async with httpx.AsyncClient() as client:
              resp = await client.get(url)
              data = resp.json()
              result = f"The IP address of the user is: {data['ip']}"
          except Exception as e:
            result = f"Failed to get IP address: {str(e)}"
        elif tool_name == "get_isp_details":
          try:
              url_template = get_config("isp_api_url")
              async with httpx.AsyncClient() as client:
                  resp = await client.get(url_template.format(args['ip']))
                  data = resp.json()
                  if data.get("status") == "fail":
                      result = f"Could not retrieve details for {args['ip']}: {data.get('message', 'Unknown error')}"
                  else:
                      result = f"ISP Details for {data.get('query')}: {data.get('isp')} ({data.get('org')}) located in {data.get('city')}, {data.get('country')}."
          except Exception as e:
              result = f"Error calling ISP lookup API: {str(e)}"
        elif tool_name == "get_current_date":
            now = datetime.datetime.now()
            result = f"Today is {now.strftime('%B % d, %Y')}"
        elif tool_name == "get_usd_idr_rate":
          try:
            url = get_config("exchange_rate_url")
            async with httpx.AsyncClient() as client:
              resp = await client.get(url)
              data = resp.json()
              rate = data.get("rates", {}).get("IDR")
              result = f"The current USD to IDR exchange rate is: {rate:,.2f} IDR"
          except Exception as e:
            result = f"Failed to fetch exchange rate: {str(e)}"
        elif tool_name == "get_gold_btc_prices":
          try:
            url = get_config("market_price_url")
            factor = float(get_config("gold_conversion_factor", 31.1034768))
            async with httpx.AsyncClient() as client:
              resp = await client.get(url)
              if resp.status_code == 429:
                  result = "Failed to fetch market prices: Rate limited by CoinGecko. Please try again in a minute."
              else:
                  data = resp.json()
                  btc_price = data.get("bitcoin", {}).get("usd")
                  gold_price_oz = data.get("pax-gold", {}).get("usd")
                  
                  if not btc_price or not gold_price_oz:
                      result = "Failed to fetch market prices: API returned incomplete data."
                  else:
                      gold_price_gram = gold_price_oz / factor
                      
                      result = (
                        f"Market Update ({datetime.datetime.now().strftime('%H:%M')}):\n"
                        f"- Bitcoin (BTC): ${btc_price:,.2f} USD\n"
                        f"- Gold (Spot): ${gold_price_gram:,.2f} USD per gram (derived from ${gold_price_oz:,.2f}/oz spot price)"
                      )
          except Exception as e:
            result = f"Failed to fetch market prices: {str(e)}"
        elif tool_name == "currency_calculator":
          try:
            amount = args.get("amount", 0)
            rate = args.get("rate", 0)
            label = args.get("label", "units")
            total = amount * rate
            result = f"Calculation: {amount:,.4f} x {rate:,.4f} = {total:,.2f} {label}"
          except Exception as e:
            result = f"Math error: {str(e)}"
        elif tool_name == "get_weather":
            city = args.get("city", "Unknown City")
            temp = (len(city) * 3) % 15 + 15
            conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Light Breeze"][len(city) % 5]
            humidity = (len(city) * 7) % 40 + 40
            result = f"Current weather in {city}: {conditions}, {temp}°C, Humidity: {humidity}%."
        elif tool_name == "web_search":
            query = args.get("query", "")
            if "ollama" in query.lower():
                result = "Ollama is an open-source tool that allows you to run open-source large language models locally."
            elif "weather" in query.lower():
                result = "Latest weather news: Unusual warm front moving across the northern hemisphere."
            else:
                result = f"Search results for '{query}': Found 3 highly relevant articles discussing {query} in modern contexts."
        else:
            result = "Tool not found"
            
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "content": [{"type": "text", "text": result}]
            }
        }

    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
