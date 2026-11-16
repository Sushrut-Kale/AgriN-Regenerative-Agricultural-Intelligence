#ifndef AGRISENSE_TELEMETRY_BUFFER_H
#define AGRISENSE_TELEMETRY_BUFFER_H

#include <string>
#include <vector>
#include <deque>
#include <stdint.h>
#include "telemetry.h"

class TelemetryBuffer {
public:
    explicit TelemetryBuffer(size_t max_capacity = 120);

    bool init();
    bool push(const TelemetryPacket& packet);
    bool pop(TelemetryPacket& out_packet);
    bool peek(TelemetryPacket& out_packet) const;
    void removeFront();
    size_t count() const;
    bool isFull() const;
    bool isEmpty() const;
    void clear();

private:
    size_t m_max_capacity;
    std::deque<TelemetryPacket> m_queue;
};

#endif // AGRISENSE_TELEMETRY_BUFFER_H
