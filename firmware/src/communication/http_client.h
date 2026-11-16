#ifndef AGRISENSE_HTTP_CLIENT_H
#define AGRISENSE_HTTP_CLIENT_H

#include <string>
#include <stdint.h>
#include "telemetry.h"
#include "authentication.h"

struct HttpResponse {
    int status_code = 0;
    std::string body;
    bool success = false;
    std::string error_message;
};

class HttpClient {
public:
    HttpClient(const std::string& base_url, const Authentication& auth);

    HttpResponse postTelemetry(const TelemetryPacket& packet);
    HttpResponse postHeartbeat(const HeartbeatPacket& heartbeat);

    void setBaseUrl(const std::string& url) { m_base_url = url; }

private:
    std::string m_base_url;
    Authentication m_auth;

    HttpResponse executePost(const std::string& url, const std::string& json_payload);
};

#endif // AGRISENSE_HTTP_CLIENT_H
