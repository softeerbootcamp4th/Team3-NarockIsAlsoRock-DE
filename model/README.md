# Model
## EDA
- EDA 결과 정리 - ([범규](https://github.com/nothingmin/softeer-team-project/tree/main/model/EDA/bg), [구](https://github.com/nothingmin/softeer-team-project/tree/main/model/EDA/gu), [우형](https://github.com/nothingmin/softeer-team-project/tree/main/model/EDA/wh))
- EDA 결과를 바탕으로, 시간의 흐름에 따른 게시물의 댓글 수 변화에 기반한 화제성 평가 지표를 정의하였다.
- "화제성이 높은 게시물"의 기준을 조회수 또는 댓글수 상위 3% 이상인 게시물로 정의하였다.
- 화제성이 높은 게시물을 hot post, 그렇지 않은 게시물을 cold post로 지칭한다.

## Modeling
- 과거 게시물들을 hot post와 cold post로 구분한다.
- 이후, 각 게시물들의 시간대 별 누적 댓글 수를 측정한다.
- 게시물들 간의 동일한 비교를 위해, 시간대는 댓글 작성 시간에서 게시물 작성 시간을 뺀 상대 시간을 이용한다.
- 시간대 별 누적 댓글수의 통계적 특성을 기반으로, normal distribution의 pdf를 구한다.
- 그 결과는 아래와 같다.

|상대 시간 (분)|결과|
|:------:|:---:|
|0~4| ![0](https://github.com/user-attachments/assets/01357711-8d46-452f-a027-f0ede8e62f40)|
|30~34| ![30](https://github.com/user-attachments/assets/f826e21b-5462-4a17-96e0-75cc0919a0a0)|
|60~64|![60](https://github.com/user-attachments/assets/bc6bdb57-c0ad-4af7-b148-daa4f1543c44)|
|90~94|![90](https://github.com/user-attachments/assets/1e8d0c70-afa1-4cd9-8527-fa1eabcce279)|
|720~724|![720](https://github.com/user-attachments/assets/45719c17-9b21-475f-8ff7-9c6f8222f5e2)|

## Setting Impact Criteria via Model
- 위의 모델을 통해 각 게시물의 영향력을 하나의 정량적인 지표로 표현하고자 한다.
- 각 게시물의 영향력은 게시물이 작성된 시점으로 부터 현 시점까지의 시간, 게시물에 달린 댓글 수, 그리고 위에서 정의한 모델(hot post, cold post의 pdf)을 통해 결정된다.
- 게시물이 작성된 시점으로 부터 현 시점까지의 시간을 통해 2개의 pdf(hot/cold post)를 선택하고, 게시물에 달린 댓글 수를 이용하여 각각의 확률을 추정한다.
- 이후, hot post일 확률을 cold post일 확률로 나눈 값에 log를 취한 값을 impact로 사용한다.
- 그 결과는 아래와 같다.
- 같은 댓글 수를 가진 게시물일지라도, 해당 댓글 수를 달성할 때 까지 소요된 시간을 반영하여 impact를 표현할 수 있다는 것을 확인할 수 있다.

|상대 시간 (분)|결과|
|:------:|:---:|
|0~4| ![0](https://github.com/user-attachments/assets/5f9dbac0-b038-41a1-ba1c-ce0df2a9cf2b)|
|30~34|![30](https://github.com/user-attachments/assets/7589a1d7-ce90-4405-a1f2-c3839abfe959)|
|60~64|![60](https://github.com/user-attachments/assets/4a8c67bd-0e06-480e-ba83-14c42d6e22f2)|
|90~94|![90](https://github.com/user-attachments/assets/86601b08-37df-45c0-b333-013db6c63521)|
|720~724|![720](https://github.com/user-attachments/assets/94ab5af3-6013-4c11-b037-23ef479f00c4)|

## Spark job
- 위에서 설정한 impact 값을 EMR에서 계산할 수 있도록, [spark job](https://github.com/nothingmin/softeer-team-project/tree/main/model/spark-job)을 작성하였다. 