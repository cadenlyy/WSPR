import urllib.request
import json

#   name             type
#|id        |UInt64                |
#|time      |DateTime              |
#|band      |Int16                 |
#|rx_sign   |LowCardinality(String)|
#|rx_lat    |Float32               |
#|rx_lon    |Float32               |
#|rx_loc    |LowCardinality(String)|
#|tx_sign   |LowCardinality(String)|
#|tx_lat    |Float32               |
#|tx_lon    |Float32               |
#|tx_loc    |LowCardinality(String)|
#|distance  |UInt16                |
#|azimuth   |UInt16                |
#|rx_azimuth|UInt16                |
#frequency  |UInt32                |
#|power     |Int8                  |
#|snr       |Int8                  |
#|drift     |Int8                  |
#|version   |LowCardinality(String)|
#|code      |Int8                  |

def wsprlive_get(col, database, ts, te, l=100):
    # put together the request url
    q = "SELECT " + col + " FROM " + database + " WHERE time >= '" + ts + "' AND time < '" + te + "' Limit " + str(l)

    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(q + " FORMAT JSON")

    # download contents from wspr.live
    contents = urllib.request.urlopen(url).read()

    # return the json decoded data
    return json.loads(contents.decode("UTF-8"))["data"]

#test
if __name__ == "__main__":
    #print(wsprlive_get("DESC wspr.rx"))
    print(wsprlive_get("*", "rx", '2024-07-24 09:05:00', '2024-07-24 09:06:00', 10))
