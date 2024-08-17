# 주제
현대 자동차에서 신규 모델이 출시되었을 때 SNS (유튜브, 인스타 그램, 커뮤니티 등)에서 해당 모델에 대한 소비자들의 반응을 모니터링해서 특정 이슈에 대한 대화가 얼마나 이루어지고 있는지를 모니터링하고 알림을 제공하는 Data Product

## SNS 데이터의 특성
- SNS 데이터에서는 소비자들의 반응과 감정을 **실시간**으로 확인할 수 있다.
- 커뮤니티의 반응을 실시간으로 모니터링함으로써, 현대자동차 관련 이슈가 화재가 되기 전에 미리 알람을 제공하여 PR팀의 빠른 대처가 가능하도록 한다. 
- 하지만, SNS 데이터에서 얻을 수 있는 소비자의 반응(조회수, 공감수 등)은 대부분 누적합으로 표시되어, 시간의 흐름에 따른 변화를 알기 어렵다.

## 커뮤니티 선정
- 자동차에 관심이 많은 사람들이 주를 이루는 커뮤니티를 선정하여 크롤링 한다.
    - 클리앙, 보배드림, fm코리아, 네이버 카페 (전기차 동호회)

## SNS 이슈 사례 선정
- 벤츠 화재
- 아이오닉 누수
- 아이오닉 iccu
- 코나 화재

## SNS 상에서의 이슈 패턴
- 하나의 제보성 글이 올라오면 뜨거운 반응을 얻고, 그 후 관련 게시물들이 더욱 많이 등장한다.

## 사례 분석
### 화재성 분석
- 일별 관련 게시물의 수, 좋아요 수, 조회 수, 댓글 수를 기준으로 화재성에 대한 시각화 진행

#### 벤츠 화재
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/b27bb594-9bde-46f7-8e9e-0d13524bc6c6)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/537518eb-4f9e-4c7d-adab-3edfd7cd21de)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/5612b55e-610f-41ef-bb69-40e54a3a2c37)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/989892a0-170d-4282-9bff-94bb2817e0bc)

#### 아이오닉 누수
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/a2e777d1-09e4-447e-adc4-4a9aea0f2ad5)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/66fe35a2-0cfa-458c-bd6d-f1f076fa0d3b)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/37507730-b4cb-4216-be59-af2d5e67e2f3)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/6cfebae4-3488-4e76-b033-14c5483debbd)

#### 아이오닉 iccu
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/1dedb9e1-e914-4530-8997-1e337b96a45f)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/b74dcf6c-4679-4f65-82bb-09b6b6ab0363)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/2000a0f2-1de2-40e0-8d33-44750283e2b3)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/4b125dc2-c34d-418c-a851-fe35cd506354)

#### 코나 화재
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/0660b99a-65e9-4225-8be6-2217aa2f5b03)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/cb8bbe2c-0d8f-4011-b877-56505f6cf6eb)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/04707d75-19d9-4c4a-bd31-ca8b362225ab)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/4a8ce368-5ab8-4de7-8380-38ee9dfb153f)

#### 결론
- 일별 댓글 수 추이는 일별 관련 키워드가 포함된 관련 게시물의 수, 해당 게시물들의 조회 수 추이와 유사한 양상을 보인다.
- 시간의 흐름에 따른 변화를 알 수 있는 것은 댓글 뿐이지만, 게시물의 댓글 수에 급격한 변화가 발생하는 경우 공감하는 사람들의 수가 그만큼 많다고 판단할 수 있다.
