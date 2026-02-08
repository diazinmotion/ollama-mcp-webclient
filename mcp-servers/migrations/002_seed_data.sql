-- Seed initial configurations
INSERT OR IGNORE INTO configs (key, value) VALUES ('gold_conversion_factor', '31.1034768');
INSERT OR IGNORE INTO configs (key, value) VALUES ('ip_api_url', 'https://api.ipify.org/?format=json');
INSERT OR IGNORE INTO configs (key, value) VALUES ('exchange_rate_url', 'https://api.exchangerate-api.com/v4/latest/USD');
INSERT OR IGNORE INTO configs (key, value) VALUES ('market_price_url', 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,pax-gold&vs_currencies=usd');
INSERT OR IGNORE INTO configs (key, value) VALUES ('isp_api_url', 'http://ip-api.com/json/{}?fields=status,message,country,regionName,city,isp,org,as,query');
INSERT OR IGNORE INTO configs (key, value) VALUES ('model', 'qwen2.5:1.5b');
INSERT OR IGNORE INTO configs (key, value) VALUES ('temperature', '0.7');
INSERT OR IGNORE INTO configs (key, value) VALUES ('top_k', '40');

-- Seed initial tools
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_current_time', 'Get current local time and date. Use this for ANY questions about time, date, day, month or year.', '{"type": "object", "properties": {}}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_current_date', 'Get the current date (Year, Month, Day). Use this for any date-related queries.', '{"type": "object", "properties": {}}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_weather', 'Get current weather for a city (simulations).', '{"type": "object", "properties": {"city": {"type": "string", "description": "The city name"}}, "required": ["city"]}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('web_search', 'Search the web for real-time information and news.', '{"type": "object", "properties": {"query": {"type": "string", "description": "The search query"}}, "required": ["query"]}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_ip', 'Get the IP address of the user.', '{"type": "object", "properties": {}}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_isp_details', 'Get the ISP details of the user.', '{"type": "object", "properties": {"ip": {"type": "string", "description": "The IP address of the user"}}, "required": ["ip"]}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_usd_idr_rate', 'Fetch the current exchange rate from USD to IDR.', '{"type": "object", "properties": {}}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('get_gold_btc_prices', 'Fetch the current real-time prices for Gold (per gram) and Bitcoin (BTC) in USD.', '{"type": "object", "properties": {}}');
INSERT OR IGNORE INTO tools (name, description, input_schema) VALUES ('currency_calculator', 'Calculate currency conversions or unit multiplication with high precision.', '{"type": "object", "properties": {"amount": {"type": "number", "description": "The numeric value to transform"}, "rate": {"type": "number", "description": "The exchange rate or multiplier"}, "label": {"type": "string", "description": "Optional label like \"IDR\""}}, "required": ["amount", "rate"]}');
