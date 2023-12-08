from Controller.website2_WPH import send_request_WPH


def test_WPH_api():
    assert send_request_WPH("nike运动鞋") == [
        [
            "COURT LEGACY 轻便休闲 小白鞋 男子板鞋",
            "Nike",
            "188",
            "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/611861/2023/0612/178/4b8049eb-ea43-4631-8e1d-e83f44c4b5f1.jpg",
            "板鞋/小白鞋,平底,无,适中",
            "https://detail.vip.com/detail-1710618487-6920028890971952983.html",
        ],
        [
            "AIR RIFT BR 轻便网面 运动休闲女鞋",
            "Nike",
            "198",
            "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvop/00611861/10000630/476003720-2383607089733115906-2383607089733115916-1.jpg",
            "休闲鞋,平底,无,适中",
            "https://detail.vip.com/detail-1710618487-6919225924299228503.html",
        ],
        [
            "男款运动休闲低帮小白鞋板",
            "Nike",
            "210",
            "http://h2.appsimg.com/a.appsimg.com/upload/merchandise/pdcvis/2022/04/13/131/70789aa9-235e-42a5-839c-f11d06fa469f.jpg",
            "休闲鞋,平底,适中,系带",
            "https://detail.vip.com/detail-1712010652-6919796895719061084.html",
        ],
    ]
