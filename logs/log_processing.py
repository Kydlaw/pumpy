import re


def get_ids(path):
    ids = list()
    with open(path, "r") as log_file:
        for log in log_file:
            result = re.search(r"\d{5,}", log)
            if result:
                ids.append(result.group(0))
    return ids


def remove_lost_tweets(path_originals, path_losts, path_availables):
    original_ids = get_ids(path_originals)
    losts_ids = get_ids(path_losts)
    with open(path_availables, "w") as available_ids:
        for line in original_ids:
            if line not in losts_ids:
                available_ids.write(line + "\n")


if __name__ == "__main__":
    path1 = "./tweets_not_found.log"
    path2 = "../data/CrisisLexT26/2012_Colorado_wildfires/available_ids.txt"
    path3 = "../data/CrisisLexT26/2012_Colorado_wildfires/2012_Colorado_wildfires-tweetids_entire_period.csv"

    remove_lost_tweets(path3, path1, path2)

