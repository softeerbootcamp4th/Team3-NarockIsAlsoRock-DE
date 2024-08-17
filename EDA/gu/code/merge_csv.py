import os
import pandas as pd

events = ["벤츠 화재", "아이오닉 누수", "아이오닉 iccu", "코나 화재"]
for event in events:
    os.makedirs(f"../data/{event}", exist_ok=True)
    communities = ["bobae", "clien", "fmkorea", "naver_cafe"]
    for community in communities:
        root_folder_path = f"../../../resources/{event}/{community}"

        csv_posts_files = []
        csv_comments_files = []

        for root, dirs, files in os.walk(root_folder_path):
            for file in files:
                if "posts" in root and file.endswith(".csv"):
                    csv_posts_files.append(os.path.join(root, file))
                elif "comments" in root and file.endswith(".csv"):
                    csv_comments_files.append(os.path.join(root, file))

        dfs = []
        for csv_file in csv_posts_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)

        output_file = f"../data/{event}/{community}_posts.csv"
        combined_df.to_csv(output_file, index=False)

        dfs = []
        for csv_file in csv_comments_files:
            df = pd.read_csv(csv_file)
            dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)

        output_file = f"../data/{event}/{community}_comments.csv"
        combined_df.to_csv(output_file, index=False)