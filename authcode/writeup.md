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

## find WinMain
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

## lpfnWndProc
`.140001ea0` 함수에서는 폼을 생성하는 코드, 종료하는 코드도 있는데,
여기서 가장 중요한 생성 함수를 눌렀을 때의 코드가 있다.

```c++
::hWnd = CreateWindowExW(0, L"Edit", &word_140004520, 0x50800000u, 90, 10, 200, 20, hWndParent, 0i64, v7, 0i64);
```
```c++
qword_140006798 = CreateWindowExW(0, L"Edit", &word_140004520, 0x50800000u, 90, 50, 200, 20, hWndParent, 0i64, v9, 0i64);
```
이 두 부분이 입력 폼을 만드는 부분이다.

```c++
CreateWindowExW(0, L"Button", "생성", 0x50000000u, 230, 80, 60, 25, hWndParent, (HMENU)3, v10, 0i64);
```
이 부분은 생성 버튼을 만드는 부분이다.

아래쪽에 a2 == 0x111, a3 == 3 인 곳에 `.140001b90`을 호출하는데
이것이 바로 생성 버튼을 누를 때 실행되는 함수이다.

다음 단계로 넘어가기 전에 자동으로 변수명이 지정된
`hWnd`는 `goyu_edit`으로, qword_140006798은 `bimil_edit`으로 바꿔준다.

# 생성 함수 분석

## 제한 (invalid format이 뜨지 않게)

그래프를 보면 대충 감이 오겠지만, 안쪽에서 분기문 조건에 안 맞거나
break이 이루어지면 invalid format이 뜬다.

그래서 조건을 몇개 보면 다음과 같다.

### 고유번호 길이
```c++
if ( GetWindowTextLengthA(goyu_edit) == 14 )
```
고유번호의 길이는 information.txt에서 봤듯이 14자리여야한다

### 고유번호 포맷 (대쉬)
```c++
if ( v4[4] == 45 && v4[9] == 45 )
```
5번째와 10번째 글자는 45(-)여야한다.

### 고유번호 포맷 (16진수)
```c++
if ( v8 != 4 && v8 != 9 )
{
    v9 = v4[v8];
    if ( (unsigned __int8)(v9 - 48) > 9u && (unsigned __int8)(v9 - 65) > 5u )
        break;
}
```
숫자가 이거나 A~F중 하나여야한다.

## 흐름 분석

### 초기화
```c++
v1 = hWnd;
v24 = 1779033703;
v2 = 0i64;
v32 = 0;
v25 = -1150833019;
v26 = 1013904242;
v27 = -1521486534;
v28 = 1359893119;
v29 = -1694144372;
v30 = 528734635;
v31 = 1541459225i64;
```
각종 값들을 설정하는 단계이다.
이 숫자들은 나중에 쓰인다.

### 글자 가져오기
```c++
v4 = (CHAR *)sub_1400021E4(0x10ui64);
GetWindowTextA(goyu_edit, v4, 15);
v5 = GetWindowTextLengthA(bimil_edit);
v6 = sub_1400021E4((signed int)(v5 + 2));
GetWindowTextA(bimil_edit, (LPSTR)v6, v5 + 1);
HIDWORD(v31) += v5 >> 29;
v32 += 8 * v5;
```
폼에서 문자열을 가져오는 부분이다.
`.1400021e4`는 들어가보면 size를 받는 것으로 보아, `malloc`함수이다.
(_malloc으로 이름을 바꿔주자)

밑에 두줄은 비밀번호 길이를 가지고 무언가를 설정하고 있다.

### ???
```c++
if ( v5 >= 0x40 ) {
    v7 = (unsigned __int64)v5 >> 6;
    do {
        Dst = *(_OWORD *)v6;
        v34 = *(_OWORD *)(v6 + 16);
        v35 = *(_OWORD *)(v6 + 32);
        v36 = *(_OWORD *)(v6 + 48);
        sub_140001000(&Dst, &v24);
        v6 += 64i64;
        v5 -= 64;
        --v7;
    } while ( v7 );
}
```

비밀번호 길이가 0x40이 넘으면 뭔가 이상한 함수를 실행시킨다.
하지만 실제 프로그램에서는 0x40이상 입력할 수가 없게 되어있다.

지금은 이 부분을 넘기지만 나중에 `.140001000` 함수를 분석해야한다.

### 스택으로
```c++
memcpy(&Dst, (const void *)v6, v5);
```
비밀번호를 스택에 있는 Dst에 저장한다.

---

여기 아래 부분은 실제로 생성하는 코드이다.

---

### 크게 크게 나누기

여러 줄이 있지만 사실 앞부분 토큰을 구하는 로직과 뒷부분 토큰을 구하는 로직이 분리 되어있다.

`.140001760`을 호출 하기 전, 그리고 `malloc`을 호출하기 전 이렇게
세 부분으로 나눠볼 수 있다.

첫번째 부분은 현재 시각을 가지고 이것저것 하는 것 처럼 보이고
두번째 부분은 xmm레지스터를 이용한 연산으로 보이고
세번째 부분은 첫번째 두번째에서 만든 것을 합치는 것이라고 보면 된다.

지금 여기서 보이는 두개 함수에 이름을 붙여줄 수 있다.

* `.140001900` -> sscanf
* `.1400018a0` -> sprintf


## 세번째 부분
세번째 부분을 먼저 보고 나머지를 분석하는게 도움이 될 것이다.

```c++
v3 = (char *)malloc(0xAui64);
v20 = (unsigned int)v11;
v21 = v10 & 0x100;
v22 = (unsigned int)v19;
if ( !v21 )
    v22 = (unsigned int)v20;
if ( !v21 )
    v20 = (unsigned int)v19;
sprintf(v3, "%04hX-%04hX", v20, v22);
```

첫번째 두번째 부분에서 만들어진 v10, v11과 v19라는 변수를 가지고 만드는데,
`v10 & 0x100`을 한 결과가 0이면 `{두번째 hex}-{첫번째 hex}` 꼴이 되고
0이 아니면 `{첫번째 hex}-{두번째 hex}`꼴이 된다.

## 첫번째 부분

> [Doc](https://docs.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getsystemtimeasfiletime)
<- 한번 읽고 오는 것도?

FILETIME 구조체 포인터를 받아서 현재 시스템 시간을 넣어준다는 그 소리

```c++
sscanf(v4, "%hx-%hx-%hx", &v37, &v38, &v39);
GetSystemTimeAsFileTime(&SystemTimeAsFileTime);
v10 = (*&SystemTimeAsFileTime - 116444736000000000i64) / 6000000000i64;
v11 = v39 ^ v38 ^ v37 * (unsigned __int8)v10;
```

딱 봐도 수를 계산하는게 복잡해 보인다.

그래서 똑같은 코드를 직접 visual c++로 만들어서 돌려보았다.

```c++
#include <windows.h>
#include <stdio.h>

int main(void) {
	FILETIME a;
	GetSystemTimeAsFileTime(&a);
	long long b = *((long long*)&a);
	b = (b - 116444736000000000l) / 6000000000l;
	printf("%lld\n", b);
}
```
컴퓨터 시각을 문제에서 나온 `2020-09-11 20:17:15+0900`으로 맞춰놓고 돌리니 `2666371`이 나왔다.

고유 번호 일부분이 주어지고 시각을 아니깐
주어진 바이너리에서 v37, v38, v10의 값은 아는 상태이다.

이때 `v10 & 0x100`은 0이 아니므로 결과값인 v11도 0x6a30이 되어야 함을 알고 있다.

xor 역 연산을 하면 다음과 같은 코드로 구할 수 있다.

```python
tttt = 2666371
goyu = [0xb1c2, 0x4ea2]
print(hex(((goyu[1] ^ goyu[0] * (tttt & 0xff)) ^ 0x6a30) & 0xffff))
```

세번째 고유번호는 D2D4임을 알 수 있다.

## 두번째 부분

고유번호를 이리저리 바꾸고 컴퓨터 시각도 이리저리 바꿔본 결과,
두번째 부분은 비밀번호에 의해서만 결정된다는 것을 미리 알아냈다.
