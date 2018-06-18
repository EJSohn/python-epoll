# Python epoll

epoll 모델 async server와 simple client가 통신하는 간단예제입니다.

client - 객체가 든 딕셔너리를 pickle 모듈을 이용해 bytes화하고 전송한 뒤 종료됩니다.

server - pickling된 데이터를 받아 확인한 후 종료합니다.

## 테스트 방법

```bash
// python 3

SOCKET_PORT=8080 python async_epoll_server.py
SOCKET_PORT=8080 python simple_client.py
```