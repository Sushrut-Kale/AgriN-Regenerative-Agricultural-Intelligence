#ifndef AGRISENSE_AUTHENTICATION_H
#define AGRISENSE_AUTHENTICATION_H

#include <string>
#include <map>

class Authentication {
public:
    Authentication(const std::string& device_id, const std::string& api_key);

    std::map<std::string, std::string> getAuthHeaders() const;
    const std::string& getDeviceId() const { return m_device_id; }
    const std::string& getApiKey() const { return m_api_key; }

    void updateCredentials(const std::string& device_id, const std::string& api_key);

private:
    std::string m_device_id;
    std::string m_api_key;
};

#endif // AGRISENSE_AUTHENTICATION_H
