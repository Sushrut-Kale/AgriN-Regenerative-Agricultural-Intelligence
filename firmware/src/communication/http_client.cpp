#include "http_client.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFiClient.h>
#endif

HttpClient::HttpClient(const std::string& base_url, const Authentication& auth)
    : m_base_url(base_url), m_auth(auth) {}

HttpResponse HttpClient::executePost(const std::string& url, const std::string& json_payload) {
    HttpResponse resp;

#ifdef ARDUINO
    WiFiClient client;
    HTTPClient http;

    if (!http.begin(client, url.c_str())) {
        resp.success = false;
        resp.error_message = "Failed to initialize HTTP connection";
        return resp;
    }

    http.setTimeout(10000); // 10 second timeout

    // Add headers
    auto headers = m_auth.getAuthHeaders();
    for (const auto& kv : headers) {
        http.addHeader(kv.first.c_str(), kv.second.c_str());
    }

    int httpCode = http.POST(json_payload.c_str());
    resp.status_code = httpCode;

    if (httpCode > 0) {
        resp.body = http.getString().c_str();
        resp.success = (httpCode == 200 || httpCode == 201);
        if (!resp.success) {
            resp.error_message = std::string("HTTP Error: ") + std::to_string(httpCode);
        }
    } else {
        resp.success = false;
        resp.error_message = http.errorToString(httpCode).c_str();
    }

    http.end();
#else
    // Host / simulation fallback: mock success for testing
    (void)url;
    (void)json_payload;
    resp.status_code = 201;
    resp.body = "{\"status\": \"SUCCESS\", \"telemetry_id\": \"mock-telemetry-001\"}";
    resp.success = true;
#endif

    return resp;
}

HttpResponse HttpClient::postTelemetry(const TelemetryPacket& packet) {
    std::string url = m_base_url + "/api/telemetry/ingest";
    std::string json = packet.toJson();
    return executePost(url, json);
}

HttpResponse HttpClient::postHeartbeat(const HeartbeatPacket& heartbeat) {
    std::string url = m_base_url + "/api/devices/" + m_auth.getDeviceId() + "/heartbeat";
    std::string json = heartbeat.toJson();
    return executePost(url, json);
}
