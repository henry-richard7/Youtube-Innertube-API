import requests
from time_ago_datetime import convert_time_ago


class YoutubeInnerApi:
    @staticmethod
    def get_video_metrics(video_id):
        url = "https://www.youtube.com/youtubei/v1/next?key=AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
            "cookie": "CONSENT=PENDING+911",
            "referer": "https://www.youtube.com",
            "x-youtube-client-version": "2.20230309.08.00",
            "origin": "https://www.youtube.com",
            "Content-Type": "application/json",
        }
        payload = {
            "videoId": video_id,
            "context": {
                "user": {"lockedSafetyMode": False},
                "request": {"internalExperimentFlags": [], "useSsl": True},
                "client": {
                    "platform": "DESKTOP",
                    "hl": "en-GB",
                    "clientName": "WEB",
                    "gl": "US",
                    "originalUrl": "https://www.youtube.com",
                    "clientVersion": "2.20230309.08.00",
                },
            },
        }
        result = {}
        response = requests.request("POST", url, headers=headers, json=payload).json()

        try:
            view_count = (
                response["contents"]["twoColumnWatchNextResults"]["results"]["results"][
                    "contents"
                ][0]["videoPrimaryInfoRenderer"]["viewCount"]["videoViewCountRenderer"][
                    "viewCount"
                ][
                    "simpleText"
                ]
                .replace(" views", "")
                .replace(" view", "")
                .replace(",", "")
            )

            likes_count = (
                response["contents"]["twoColumnWatchNextResults"]["results"]["results"][
                    "contents"
                ][0]["videoPrimaryInfoRenderer"]["videoActions"]["menuRenderer"][
                    "topLevelButtons"
                ][
                    0
                ][
                    "segmentedLikeDislikeButtonRenderer"
                ][
                    "likeButton"
                ][
                    "toggleButtonRenderer"
                ][
                    "defaultText"
                ][
                    "accessibility"
                ][
                    "accessibilityData"
                ][
                    "label"
                ]
                .replace(" likes", "")
                .replace(" like", "")
                .replace(",", "")
            )
            post_create_date = response["contents"]["twoColumnWatchNextResults"][
                "results"
            ]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["dateText"][
                "simpleText"
            ]
            is_premium = False
        except:
            view_count = None
            likes_count = None
            post_create_date = None
            is_premium = True

        result["video_id"] = video_id
        result["view_count"] = int(view_count) if view_count != "No" else 0
        result["likes_count"] = int(likes_count) if likes_count != "No" else 0

        try:
            comment_token = response["contents"]["twoColumnWatchNextResults"][
                "results"
            ]["results"]["contents"][-1]["itemSectionRenderer"]["contents"][-1][
                "continuationItemRenderer"
            ][
                "continuationEndpoint"
            ][
                "continuationCommand"
            ][
                "token"
            ]
            payload["continuation"] = comment_token
            response2 = requests.request(
                "POST", url, headers=headers, json=payload
            ).json()
            result["comment_count"] = int(
                response2["onResponseReceivedEndpoints"][0][
                    "reloadContinuationItemsCommand"
                ]["continuationItems"][0]["commentsHeaderRenderer"]["countText"][
                    "runs"
                ][
                    0
                ][
                    "text"
                ].replace(
                    ",", ""
                )
            )
        except Exception as e:
            # print(e, f"Comment Token: {comment_token}")
            result["comment_count"] = 0

        result["is_premium"] = is_premium
        result["post_create_date"] = post_create_date

        return result

    def get_comments(self, video_id):
        url = "https://www.youtube.com/youtubei/v1/next?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false"

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
            "cookie": "CONSENT=PENDING+911",
            "referer": "https://www.youtube.com",
            "x-youtube-client-version": "2.20230309.08.00",
            "origin": "https://www.youtube.com",
            "Content-Type": "application/json",
        }

        payload = {
            "videoId": video_id,
            "context": {
                "user": {"lockedSafetyMode": False},
                "request": {"internalExperimentFlags": [], "useSsl": True},
                "client": {
                    "platform": "DESKTOP",
                    "hl": "en-GB",
                    "clientName": "WEB",
                    "gl": "US",
                    "originalUrl": "https://www.youtube.com",
                    "clientVersion": "2.20230309.08.00",
                },
            },
        }

        comment_response = requests.request(
            "POST", url, headers=headers, json=payload
        ).json()

        try:
            comment_token = comment_response["contents"]["twoColumnWatchNextResults"][
                "results"
            ]["results"]["contents"][-1]["itemSectionRenderer"]["contents"][-1][
                "continuationItemRenderer"
            ][
                "continuationEndpoint"
            ][
                "continuationCommand"
            ][
                "token"
            ]
        except:
            return None

        comments = []
        payload["continuation"] = comment_token
        while True:
            response = requests.request(
                "POST", url, headers=headers, json=payload
            ).json()

            if response.get("onResponseReceivedEndpoints"):
                comments_endpoint = response["onResponseReceivedEndpoints"][-1]

                if comments_endpoint.get("reloadContinuationItemsCommand"):
                    contents = comments_endpoint["reloadContinuationItemsCommand"][
                        "continuationItems"
                    ]

                elif comments_endpoint.get("appendContinuationItemsAction"):
                    contents = comments_endpoint["appendContinuationItemsAction"][
                        "continuationItems"
                    ]

                jsonKey = (
                    "commentThreadRenderer"
                    if contents[0].get("commentThreadRenderer")
                    else "commentRenderer"
                )
                for comment in contents:
                    if comment.get(jsonKey):
                        comment_detail = dict()

                        comment_detail["commentAuthorName"] = comment[jsonKey][
                            "comment"
                        ]["commentRenderer"]["authorText"]["simpleText"]
                        comment_detail["authorThumbnail"] = comment[jsonKey]["comment"][
                            "commentRenderer"
                        ]["authorThumbnail"]["thumbnails"][-1]["url"]
                        comment_detail["commentText"] = comment[jsonKey]["comment"][
                            "commentRenderer"
                        ]["contentText"]["runs"][0]["text"]
                        comment_detail["commentPublishedTime"] = convert_time_ago(
                            comment[jsonKey]["comment"]["commentRenderer"][
                                "publishedTimeText"
                            ]["runs"][0]["text"]
                        )
                        comment_detail["commentPublishedTimeText"] = comment[jsonKey][
                            "comment"
                        ]["commentRenderer"]["publishedTimeText"]["runs"][0]["text"]
                        comment_detail["commentId"] = comment[jsonKey]["comment"][
                            "commentRenderer"
                        ]["commentId"]
                        comment_detail["CommentLikes"] = (
                            comment[jsonKey]["comment"]["commentRenderer"]["voteCount"][
                                "simpleText"
                            ]
                            if comment[jsonKey]["comment"]["commentRenderer"].get(
                                "voteCount"
                            )
                            else 0
                        )
                        comment_detail["CommentReplies"] = (
                            int(
                                comment[jsonKey]["comment"]["commentRenderer"][
                                    "replyCount"
                                ]
                            )
                            if comment[jsonKey]["comment"]["commentRenderer"].get(
                                "replyCount"
                            )
                            else 0
                        )
                        comments.append(comment_detail)

                if contents[-1].get("continuationItemRenderer"):
                    if contents[-1]["continuationItemRenderer"]["continuationEndpoint"][
                        "continuationCommand"
                    ].get("token"):
                        next_page_token = contents[-1]["continuationItemRenderer"][
                            "continuationEndpoint"
                        ]["continuationCommand"].get("token")
                        payload["continuation"] = next_page_token

                else:
                    break
            else:
                break
        return comments

    def get_playlist(self, playlistID):
        continuation = None

        url = "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        playlist_payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20210224.06.00",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "browseId": f"VL{playlistID.replace('UC','UU')}",
            "params": "wgYCCAA%3D",
            "continuation": continuation,
        }
        results = list()

        while True:
            playlist_response = requests.request(
                "POST", url, json=playlist_payload
            ).json()
            if not continuation:
                items = playlist_response["contents"]["twoColumnBrowseResultsRenderer"][
                    "tabs"
                ][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0][
                    "itemSectionRenderer"
                ][
                    "contents"
                ][
                    0
                ][
                    "playlistVideoListRenderer"
                ][
                    "contents"
                ]

                for playlistItem in items:
                    if playlistItem.get("playlistVideoRenderer"):
                        results.append(
                            {
                                "video_id": playlistItem["playlistVideoRenderer"][
                                    "videoId"
                                ],
                                "title": playlistItem["playlistVideoRenderer"]["title"][
                                    "runs"
                                ][0]["text"],
                                "thumbnail": playlistItem["playlistVideoRenderer"][
                                    "thumbnail"
                                ]["thumbnails"][-1]["url"],
                            }
                        )

                try:
                    playlist_payload["continuation"] = playlist_response["contents"][
                        "twoColumnBrowseResultsRenderer"
                    ]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"][
                        "contents"
                    ][
                        0
                    ][
                        "itemSectionRenderer"
                    ][
                        "contents"
                    ][
                        0
                    ][
                        "playlistVideoListRenderer"
                    ][
                        "contents"
                    ][
                        -1
                    ][
                        "continuationItemRenderer"
                    ][
                        "continuationEndpoint"
                    ][
                        "continuationCommand"
                    ][
                        "token"
                    ]
                    continuation = True
                    # print(playlist_payload["continuation"])
                except:
                    break
            else:
                items = playlist_response["onResponseReceivedActions"][0][
                    "appendContinuationItemsAction"
                ]["continuationItems"]
                for playlistItem in items:
                    if playlistItem.get("playlistVideoRenderer"):
                        results.append(
                            {
                                "video_id": playlistItem["playlistVideoRenderer"][
                                    "videoId"
                                ],
                                "title": playlistItem["playlistVideoRenderer"]["title"][
                                    "runs"
                                ][0]["text"],
                                "thumbnail": playlistItem["playlistVideoRenderer"][
                                    "thumbnail"
                                ]["thumbnails"][-1]["url"],
                            }
                        )

                try:
                    playlist_payload["continuation"] = playlist_response[
                        "onResponseReceivedActions"
                    ][0]["appendContinuationItemsAction"]["continuationItems"][-1][
                        "continuationItemRenderer"
                    ][
                        "continuationEndpoint"
                    ][
                        "continuationCommand"
                    ][
                        "token"
                    ]
                    continuation = True
                    # print(playlist_payload["continuation"])

                except Exception as e:
                    # print(str(e))
                    break
        return results

    def get_channel(self, channel_id: str):
        url = "https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
        channel_payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20210224.06.00",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "browseId": channel_id,
        }
        playlist_payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20210224.06.00",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "browseId": f"VL{channel_id.replace('UC','UU')}",
        }

        about_payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20210224.06.00",
                    "newVisitorCookie": True,
                },
                "user": {"lockedSafetyMode": False},
            },
            "browseId": channel_id,
            "params": "EgVhYm91dPIGBAoCEgA%3D",
        }

        channel_response = requests.request("POST", url, json=channel_payload).json()
        sub_count = channel_response["header"]["c4TabbedHeaderRenderer"][
            "subscriberCountText"
        ]["simpleText"].replace(" subscribers", "")
        if "K" in sub_count:
            spliter = sub_count.split("K")
            sub_count = float(spliter[0]) * 1e3

        elif "M" in sub_count:
            spliter = sub_count.split("M")
            sub_count = float(spliter[0]) * 1e6

        elif "million" in sub_count:
            spliter = sub_count.split("million")
            sub_count = float(spliter[0]) * 1e6

        elif "B" in sub_count:
            spliter = sub_count.split("B")
            sub_count = float(spliter[0]) * 1e9

        else:
            sub_count = float(sub_count.replace(" subscribers", ""))

        channel_meta = dict()

        channel_meta["channelName"] = channel_response["header"][
            "c4TabbedHeaderRenderer"
        ]["title"]
        channel_meta["thumbnail"] = channel_response["header"][
            "c4TabbedHeaderRenderer"
        ]["avatar"]["thumbnails"][-1]["url"]
        channel_meta["banner"] = channel_response["header"]["c4TabbedHeaderRenderer"][
            "banner"
        ]["thumbnails"][-1]["url"]
        channel_meta["description"] = channel_response["metadata"][
            "channelMetadataRenderer"
        ]["description"]
        channel_meta["subscriberCount"] = int(sub_count)

        about_response = requests.post(url, json=about_payload).json()

        views_count = (
            about_response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2][
                "tabRenderer"
            ]["content"]["sectionListRenderer"]["contents"][-1]["itemSectionRenderer"][
                "contents"
            ][
                -1
            ][
                "channelAboutFullMetadataRenderer"
            ][
                "viewCountText"
            ]
            .get("simpleText")
            .split()[0]
            .replace(",", "")
        )

        joined_date = about_response["contents"]["twoColumnBrowseResultsRenderer"][
            "tabs"
        ][-2]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][-1][
            "itemSectionRenderer"
        ][
            "contents"
        ][
            -1
        ][
            "channelAboutFullMetadataRenderer"
        ][
            "joinedDateText"
        ][
            "runs"
        ][
            -1
        ][
            "text"
        ]

        country = about_response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][
            -2
        ]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][-1][
            "itemSectionRenderer"
        ][
            "contents"
        ][
            -1
        ][
            "channelAboutFullMetadataRenderer"
        ][
            "country"
        ][
            "simpleText"
        ]

        bio = about_response["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][-2][
            "tabRenderer"
        ]["content"]["sectionListRenderer"]["contents"][-1]["itemSectionRenderer"][
            "contents"
        ][
            -1
        ][
            "channelAboutFullMetadataRenderer"
        ].get(
            "artistBio"
        )

        bio = bio["simpleText"] if bio else None

        channel_meta["viewsCount"] = int(views_count)
        channel_meta["joinedDate"] = joined_date
        channel_meta["country"] = country
        channel_meta["bio"] = bio

        playlist_response = requests.request("POST", url, json=playlist_payload).json()
        channel_meta["video_count"] = playlist_response["header"][
            "playlistHeaderRenderer"
        ]["numVideosText"]["runs"][0]["text"]
        return channel_meta
