#include "telemetry_buffer.h"

TelemetryBuffer::TelemetryBuffer(size_t max_capacity)
    : m_max_capacity(max_capacity) {}

bool TelemetryBuffer::init() {
    m_queue.clear();
    return true;
}

bool TelemetryBuffer::push(const TelemetryPacket& packet) {
    if (m_queue.size() >= m_max_capacity) {
        // Discard oldest untransmitted packet to make room for fresh telemetry
        m_queue.pop_front();
    }
    m_queue.push_back(packet);
    return true;
}

bool TelemetryBuffer::pop(TelemetryPacket& out_packet) {
    if (m_queue.empty()) {
        return false;
    }
    out_packet = m_queue.front();
    m_queue.pop_front();
    return true;
}

bool TelemetryBuffer::peek(TelemetryPacket& out_packet) const {
    if (m_queue.empty()) {
        return false;
    }
    out_packet = m_queue.front();
    return true;
}

void TelemetryBuffer::removeFront() {
    if (!m_queue.empty()) {
        m_queue.pop_front();
    }
}

size_t TelemetryBuffer::count() const {
    return m_queue.size();
}

bool TelemetryBuffer::isFull() const {
    return m_queue.size() >= m_max_capacity;
}

bool TelemetryBuffer::isEmpty() const {
    return m_queue.empty();
}

void TelemetryBuffer::clear() {
    m_queue.clear();
}
