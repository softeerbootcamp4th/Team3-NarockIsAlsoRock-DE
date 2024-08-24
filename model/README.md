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
- modeling의 결과는 아래와 같다.

|상대 시간 (분)|결과|
|:------:|:---:|
|0~4| ![0](https://github.com/user-attachments/assets/01357711-8d46-452f-a027-f0ede8e62f40)|
|30~34| ![30](https://github.com/user-attachments/assets/f826e21b-5462-4a17-96e0-75cc0919a0a0)|
|60~64|![60](https://github.com/user-attachments/assets/bc6bdb57-c0ad-4af7-b148-daa4f1543c44)|
|90~94|![90](https://github.com/user-attachments/assets/1e8d0c70-afa1-4cd9-8527-fa1eabcce279)|
|720~724|![720](https://github.com/user-attachments/assets/45719c17-9b21-475f-8ff7-9c6f8222f5e2)|