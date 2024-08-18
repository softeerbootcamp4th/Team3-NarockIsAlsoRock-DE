import os
import pandas as pd

# 루트 폴더 경로를 지정하세요.


events = ['벤츠 화재', '아이오닉 누수', '아이오닉 iccu', '코나 화재']
for event in events:
    os.makedirs(f'data/{event}', exist_ok=True)
    communities = ['naver_cafe']
    for community in communities:
        root_folder_path = f'/Users/admin/Desktop/lambda_repo/softeer-team-project/resources/{event}/{community}'

        # 모든 하위 폴더에서 CSV 파일을 찾기
        csv_posts_files = []
        csv_comments_files = []
        
        for root, dirs, files in os.walk(root_folder_path):
            for file in files:
                if 'posts' in root and file.endswith('.csv'):
                    csv_posts_files.append(os.path.join(root, file))
                elif 'comments' in root and file.endswith('.csv'):
                    csv_comments_files.append(os.path.join(root, file))

        # 각 CSV 파일을 데이터프레임으로 읽고 리스트에 저장

        dfs = []
        for csv_file in csv_posts_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)

        # 모든 데이터프레임을 하나로 합치기
        combined_df = pd.concat(dfs, ignore_index=True)

        # 합친 데이터를 새 CSV 파일로 저장
        output_file = f'data/{event}/{community}_posts.csv'
        combined_df.to_csv(output_file, index=False)
        
        
        # 각 CSV 파일을 데이터프레임으로 읽고 리스트에 저장
        dfs = []
        for csv_file in csv_comments_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)

        # 모든 데이터프레임을 하나로 합치기
        combined_df = pd.concat(dfs, ignore_index=True)

        # 합친 데이터를 새 CSV 파일로 저장
        output_file = f'data/{event}/{community}_comments.csv'
        combined_df.to_csv(output_file, index=False)