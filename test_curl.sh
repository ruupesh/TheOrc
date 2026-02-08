# Test Curl Commands for TheOrchestrator Chat API

# Test 1: Valid chat request with message
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-abc",
    "role": "human",
    "content": {
      "message": "Hello, orchestrator!"
    }
  }'

# Test 2: Chat request with HITL approval (no message)
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-abc",
    "role": "human",
    "content": {
      "hitl_approval": [
        {
          "function_id": "call_b11ab9d9f1274ffca0b2272f1d3f__thought__CrkDAb4...",
          "function_name": "find_file_path",
          "confirmed": true,
          "payload": null
        }
      ]
    }
  }'

# Test 3: Chat request with metadata
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-456",
    "session_id": "sess-xyz",
    "role": "human",
    "content": {
      "message": "Another test message",
      "metadata": {
        "source": "mobile_app",
        "version": "1.0"
      }
    }
  }'

# Test 4: Missing Authorization header (should fail)
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-abc",
    "role": "human",
    "content": {
      "message": "This should fail"
    }
  }'

# Test 5: Invalid request - no message and no hitl_approval (should fail validation)
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "session_id": "sess-abc",
    "role": "human",
    "content": {
      "metadata": {"test": true}
    }
  }'
