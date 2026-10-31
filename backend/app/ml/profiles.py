# Example-only feature definitions. These are NOT validated food/adulterant sensor profiles.
PROFILES = {
 "milk":{"features":["temperature_c","ph","conductivity_us_cm"],"units":{"temperature_c":"°C","ph":"pH","conductivity_us_cm":"µS/cm"}},
 "turmeric":{"features":["temperature_c","moisture_pct","color_index"],"units":{"temperature_c":"°C","moisture_pct":"%","color_index":"index"}},
 "chilli":{"features":["temperature_c","moisture_pct","color_index"],"units":{"temperature_c":"°C","moisture_pct":"%","color_index":"index"}},
 "honey":{"features":["temperature_c","conductivity_us_cm","moisture_pct"],"units":{"temperature_c":"°C","conductivity_us_cm":"µS/cm","moisture_pct":"%"}},
 "oil":{"features":["temperature_c","conductivity_us_cm","color_index"],"units":{"temperature_c":"°C","conductivity_us_cm":"µS/cm","color_index":"index"}}
}
