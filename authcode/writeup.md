# Basic Info
* amd64 PE file
* Not packed
* x64 Microsoft visual C++ v14
* Windows GUI

> ⚠️ 저도 처음 시도해 보는 것이 매우 많습니다.
> 최대한 자세한 내용을 쓰고자 하나,
> 설명이 부족한 부분이 많으니 이점 양해 부탁 드립니다.

![1](./images/1.png)

실행하면 위와 같이 나온다.

같이 주어지는 `information.txt` 파일을 확인하면 특정 시각에
고유번호와 비밀번호를 넣어 나오는 값이 `6A30-1099`를 만족해야 하는 것으로 보인다.

> information.txt
```
KST 2020-09-11 오후 8:17:15 6A30-1099
고유 번호 : B1C2-4EA2-....
```

그러면 이제 생성 버튼을 눌렀을 때 어떠한 일이 일어나는지를
리버싱을 통해서 알아보면 된다. => 고난의 시작

# 생성 함수 찾기

일단 visual c++을 사용한 프로그램이기 때문에,
이에 맞춰서 main함수를 찾아야 한다.

visual c++을 사용한 프로그램에서 메인 함수를 찾는 방법은
[드림핵](https://dreamhack.io/learn/23#5)에 간단히 나와있다.

`start` -> `4번째 점프` -> `.140001960`

이 함수는 WinAPI에서 WinMain이라는 함수라고 불린다.

```c++
int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpszCmdParam, int nCmdShow)
```

이 함수는 단순히 창을 생성하고 창 제목을 변경하는 등의 역할을 한다.
그 안에 `lpfnWndProc` 라는 메시지 처리 함수를 지정하는 부분이 있다.

`.140001ea0` 함수에서는 폼을 생성하는 코드, 종료하는 코드도 있는데,
여기서 가장 중요한 생성 함수를 눌렀을 때의 코드가 있다.
