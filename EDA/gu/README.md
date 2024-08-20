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
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/5612b55e-610f-41ef-bb69-40e54a3a2c37)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/989892a0-170d-4282-9bff-94bb2817e0bc)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/537518eb-4f9e-4c7d-adab-3edfd7cd21de)

#### 아이오닉 누수
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/a2e777d1-09e4-447e-adc4-4a9aea0f2ad5)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/37507730-b4cb-4216-be59-af2d5e67e2f3)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/6cfebae4-3488-4e76-b033-14c5483debbd)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/66fe35a2-0cfa-458c-bd6d-f1f076fa0d3b)

#### 아이오닉 iccu
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/1dedb9e1-e914-4530-8997-1e337b96a45f)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/2000a0f2-1de2-40e0-8d33-44750283e2b3)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/4b125dc2-c34d-418c-a851-fe35cd506354)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/b74dcf6c-4679-4f65-82bb-09b6b6ab0363)

#### 코나 화재
- 일자 별 댓글 수 추이
![number_of_comments](https://github.com/user-attachments/assets/0660b99a-65e9-4225-8be6-2217aa2f5b03)
- 일자 별 게시물 수 추이
![number_of_posts](https://github.com/user-attachments/assets/04707d75-19d9-4c4a-bd31-ca8b362225ab)
- 일자 별 조회 수 추이
![number_of_views](https://github.com/user-attachments/assets/4a8ce368-5ab8-4de7-8380-38ee9dfb153f)
- 일자 별 좋아요 수 추이
![number_of_likes](https://github.com/user-attachments/assets/cb8bbe2c-0d8f-4011-b877-56505f6cf6eb)

#### 결론
- 일별 댓글 수 추이는 일별 관련 키워드가 포함된 관련 게시물의 수, 해당 게시물들의 조회 수 추이와 유사한 양상을 보인다.
- 시간의 흐름에 따른 변화를 알 수 있는 것은 댓글 뿐이지만, 게시물의 댓글 수에 급격한 변화가 발생하는 경우 공감하는 사람들의 수가 그만큼 많다고 판단할 수 있다.
- 사례 별, 화제성이 높았던 날의 댓글 변화 추이를 확인하여 정량화된 수치를 만들면, 새롭게 올라오는 게시물들의 댓글 변화 추이와 비교하여 모니터링이 가능하다.

### 사례별 게시물 분석
#### 벤츠 화재
- 화제성이 증가한 날짜 및 게시물 (커뮤니티, post id, 제목, 링크)
    - 2024.08.02 
        1. 클리앙 (18776452), 청라 전기차 화재 주차장 수습현장 [링크](https://www.clien.net/service/board/cm_car/18776452?combine=true&q=%EB%B2%A4%EC%B8%A0+%ED%99%94%EC%9E%AC&p=3&sort=recency&boardCd=&isBoard=false)
        2. 클리앙 (18776665), 전기차 주차 당분간은 시끄럽겠네용 [링크](https://www.clien.net/service/board/cm_car/18776665?combine=true&q=%EB%B2%A4%EC%B8%A0+%ED%99%94%EC%9E%AC&p=3&sort=recency&boardCd=&isBoard=false)
        3. 네이버 카페 (1525144), 청라 전기차화재 관리사무소 보상안내 [링크](https://cafe.naver.com/ca-fe/ArticleRead.nhn?clubid=21771803&page=16&userDisplay=50&inCafeSearch=true&searchBy=0&query=%EB%B2%A4%EC%B8%A0+%ED%99%94%EC%9E%AC&includeAll=&exclude=&include=&exact=&searchdate=2024-08-012024-08-30&media=0&sortBy=date&articleid=1525144&referrerAllArticles=true)
    
#### 아이오닉 누수
- 화제성이 증가한 날짜 및 게시물 (커뮤니티, post id, 제목, 링크)
    - 2023.10.26
        1. 네이버 카페 (1319521) [제보는 MBC] 빗물 유입되는 아이오닉6‥현대차 "결함 아냐" [링크](https://cafe.naver.com/ca-fe/ArticleRead.nhn?clubid=21771803&page=4&userDisplay=50&inCafeSearch=true&searchBy=0&query=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+%EB%88%84%EC%88%98&includeAll=&exclude=&include=&exact=&searchdate=2023-08-312024-02-29&media=0&sortBy=date&articleid=1319521&referrerAllArticles=true)
        2. 클리앙 (18387260) 빗물 유입되는 아이오닉6‥현대차 '결함 아냐' [링크](https://www.clien.net/service/board/park/18387260?combine=true&q=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+%EB%88%84%EC%88%98&p=1&sort=recency&boardCd=&isBoard=false)
        3. 클리앙 (18386985) 방금 mbc뉴스 아이오닉6 누수.. [링크](https://www.clien.net/service/board/park/18386985?combine=true&q=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+%EB%88%84%EC%88%98&p=1&sort=recency&boardCd=&isBoard=false)

#### 아이오닉 iccu
- 화제성이 증가한 날짜 및 게시물 (커뮤니티, post id, 제목, 링크)
    - 2024.02.20
        1. 클리앙 (18597103) 2024 전기차 보조금 확정 [링크](https://www.clien.net/service/board/park/18597103?combine=true&q=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+iccu&p=8&sort=recency&boardCd=&isBoard=false)
        2. 클리앙 (18597684) 아이오닉5 ICCU 결함 당첨 이네요 [링크](https://www.clien.net/service/board/cm_car/18597684?combine=true&q=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+iccu&p=7&sort=recency&boardCd=&isBoard=false)
        3. 네이버 카페 (1398628) iccu 글 보자마자 제차가 똑같이 됐어요 [링크](https://cafe.naver.com/ca-fe/ArticleRead.nhn?clubid=21771803&page=2&userDisplay=50&inCafeSearch=true&searchBy=0&query=%EC%95%84%EC%9D%B4%EC%98%A4%EB%8B%89+iccu&includeAll=&exclude=&include=&exact=&searchdate=2023-08-312024-02-29&media=0&sortBy=date&articleid=1398628&referrerAllArticles=true)

#### 코나 화재
- 화제성이 증가한 날짜 및 게시물 (커뮤니티, post id, 제목, 링크)
    - 2020.10.04
        1. 네이버 카페 (513046) 자동차리콜센터 코나ev 결함신고 협조 요청 [링크](https://cafe.naver.com/ca-fe/ArticleRead.nhn?clubid=21771803&page=27&userDisplay=50&inCafeSearch=true&searchBy=0&query=%EC%BD%94%EB%82%98+%ED%99%94%EC%9E%AC&includeAll=&exclude=&include=&exact=&searchdate=2020-07-312021-01-31&media=0&sortBy=date&articleid=513046&referrerAllArticles=true)
        2. 네이버 카페 (513112) 코나 내일 계약하는데ㅜ [링크](https://cafe.naver.com/ca-fe/ArticleRead.nhn?clubid=21771803&page=27&userDisplay=50&inCafeSearch=true&searchBy=0&query=%EC%BD%94%EB%82%98+%ED%99%94%EC%9E%AC&includeAll=&exclude=&include=&exact=&searchdate=2020-07-312021-01-31&media=0&sortBy=date&articleid=513112&referrerAllArticles=true)
        3. 클리앙 (15445104) 코나 전기차, 대구서 완속충전 후 화재...벌써 12번째 [링크](https://www.clien.net/service/board/cm_car/15445104?combine=true&q=%EC%BD%94%EB%82%98+%ED%99%94%EC%9E%AC&p=25&sort=recency&boardCd=&isBoard=false)

### 사례별 댓글 추이 시각화
| |continuous (x-axis: nanosecond, y: number of comments) | discrete (x-axis: 30 minutes, y: number of comments)|
|--|--|--|
|벤츠 화재|![first](https://github.com/user-attachments/assets/22f33706-a26d-4d20-a07d-9871576e9b50)|![first](https://github.com/user-attachments/assets/ecf5b98e-ed05-4408-b45c-0d48d4d50fb2)|
|아이오닉 누수|![first](https://github.com/user-attachments/assets/33c26949-3d25-4a57-9f39-fb11cc12e56d)|![first](https://github.com/user-attachments/assets/b7e8d233-0281-4270-bae9-6d13f11e4b0f)|
|아이오닉 iccu|![first](https://github.com/user-attachments/assets/9d21457c-9700-4546-9efc-1acda4066148)|![first](https://github.com/user-attachments/assets/9ccdd16b-1000-4e61-8426-306c3c3c6ca2)|
|코나|![first](https://github.com/user-attachments/assets/b0662d39-7941-4145-8ff5-92816b74212a)|![first](https://github.com/user-attachments/assets/01c44408-ffdb-48e1-b6a3-f6ccb20a7878)|

## Modeling
| 모든 그래프에서, x-axis의 unit은 30분이다.

- SNS에서 크롤링한 데이터에서 얻을 수 있는 정보는 다양하지만, 시간의 흐름에 따른 반응을 볼 수 있는 것은 댓글 밖에 없다.
- EDA를 통해 댓글 수와 조회수 사이에 큰 상관관계가 있음을 확인했으므로, 댓글 수의 변화를 통해 화제성을 추정할 수 있다고 가정한다.
- 기존의 사례들을 기반으로 크롤링한 데이터를, 화제성 있는 게시물과 그렇지 않은 게시물로 구분한다.
- 화제성 있는 게시물의 기준은, 전체 데이터를 기준으로 조회수 상위 3% 이상 또는 댓글 수 상위 3% 이상인 게시물로 한다.
- 화제성이 있는 게시물(hot post)과 그렇지 않은 게시물(cold post)의 시간의 흐름에 따른 댓글 수 변화에 대한 통계를 기반으로, curve fitting을 진행한다.

|Hot Posts| Cold Posts|
|--|--|
|![distirib_of_num_of_cmt_hot](https://github.com/user-attachments/assets/8cea6824-7f56-40a0-977c-f8c4ed551c0e)| ![distirib_of_num_of_cmt_cold](https://github.com/user-attachments/assets/01bf2c7e-9dc5-49c3-8903-f1c1335227a4)|
|![distirib_of_num_of_cmt_hot_with_pred](https://github.com/user-attachments/assets/7560ff7b-0dc6-4968-9bec-ec81a18d4ae6)|![distirib_of_num_of_cmt_cold_with_pred](https://github.com/user-attachments/assets/de2efc0e-7fcc-4cb3-9369-1e6039b4fb4a)| 

- Estimated function
    > Hot Posts: 6.27 * exp(-0.50 * (x - 1.57)) + 1.31   
    > Cold Post: 0.20 * exp(-0.89 * (x - 3.69)) + 0.18

- 새롭게 모니터링하는 게시물의 작성 시간과 댓글의 작성 시간을 기반으로, 해당 게시물의 댓글 반응 양상이 hot post와 유사한지, cold post와 유사한지를 기반으로 게시물의 영향력을 판단한다.   
![final](https://github.com/user-attachments/assets/870588f6-dd08-46ee-aa69-a790093aaf90)

