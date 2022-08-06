import fetch
DI = fetch.DI

testURLs: dict[DI, str] = {
    DI.ELCORTEINGLES: "https://www.elcorteingles.es/electronica/A43663538-tv-oled-139-cm-55-sony-xr-55a84k-bravia-google-tv-4k-hdr-xr-cognitive-processor-xr-triluminos-pro-hands-free-voice-search/?color=Negro&parentCategoryId=999.52195013",
    DI.AMAZON: "https://www.amazon.es/TD-Systems-Televisores-Chromecast-K32DLC16GLE/dp/B09YVJM363",
    DI.PCCOMPONENTES: "https://www.pccomponentes.com/gigabyte-geforce-rtx-3060-gaming-oc-12gb-gddr6-rev-20",
    DI.ZALANDO: "https://www.zalando.es/nike-sportswear-air-force-1-gtx-unisex-zapatillas-anthraciteblackbarely-grey-ni115o01u-q11.html",
    DI.WORTEN: "https://www.worten.es/productos/belleza-salud-y-bebe/salud-belleza/bascula/bascula-agd-precision-agd-joyeria-MRKEAN-8436538305003",
    DI.CARREFOUR: "https://www.carrefour.es/robot-aspirador-y-friegasuelos-irobot-roomba-combo-r113840/VC4A-12554588/p",
    DI.NIKE: "https://www.nike.com/es/t/air-force-1-07-zapatillas-DMJP7P/CW2288-111",
    DI.ADIDAS: "https://www.adidas.es/sudadera-adidas-sportswear-future-icons-3-bandas/HC5255.html",
    DI.CONVERSE: "https://www.converse.com/es/shop/p/pro-leather-mid-unisex-zapatillas-high-top/169261MP.html",
    DI.FOOTDISTRICT: "https://footdistrict.com/lourdes-men-s-graphic-t-shirt-lof1xh02ap-je130-113.html",
    DI.ALIEXPRESS: "https://es.aliexpress.com/item/1005004340051230.html",
}


class TestClass:
    # Test if any attribute is missing
    def test_domains(self):
        for url in testURLs.values():
            data = fetch.fetch_data(url)
            print(data)
            for dictio in (data.prod.__dict__, data.dom.__dict__, data.prc.__dict__):
                for val in dictio.values():
                    if val is None or val == "" or val == "None":
                        raise AssertionError(str(data.dom.name) + "." + str(data.dom.tld) + " failed: attribute is None")

