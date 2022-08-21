from concurrent.futures import ThreadPoolExecutor
import logging
import fetch
import pricelist
import multiprocessing as mp

DI = fetch.DI

testURLs: dict[DI, str] = {
    DI.ELCORTEINGLES: "https://www.elcorteingles.es/electronica/A43663538-tv-oled-139-cm-55-sony-xr-55a84k-bravia-google-tv-4k-hdr-xr-cognitive-processor-xr-triluminos-pro-hands-free-voice-search/?color=Negro&parentCategoryId=999.52195013",
    DI.AMAZON: "https://www.amazon.es/TD-Systems-Televisores-Chromecast-K32DLC16GLE/dp/B09YVJM363",
    DI.PCCOMPONENTES: "https://www.pccomponentes.com/gigabyte-geforce-rtx-3060-gaming-oc-12gb-gddr6-rev-20",
    DI.ZALANDO: "https://www.zalando.es/nike-sportswear-air-force-1-gtx-unisex-zapatillas-anthraciteblackbarely-grey-ni115o01u-q11.html",
    DI.WORTEN: "https://www.worten.es/productos/electrodomesticos/integrables/microondas-integrable-balay-3cg5172b2-20-l-con-grill-blanco-7573217",
    DI.CARREFOUR: "https://www.carrefour.es/robot-aspirador-y-friegasuelos-irobot-roomba-combo-r113840/VC4A-12554588/p",
    DI.ALIEXPRESS: "https://es.aliexpress.com/item/1005004340051230.html",
    DI.NIKE: "https://www.nike.com/es/t/air-force-1-07-zapatillas-DMJP7P/CW2288-111",
    DI.ADIDAS: "https://www.adidas.es/sudadera-adidas-sportswear-future-icons-3-bandas/HC5255.html",
    DI.CONVERSE: "https://www.converse.com/es/shop/p/pro-leather-mid-unisex-zapatillas-high-top/169261MP.html",
    DI.FOOTDISTRICT: "https://footdistrict.com/lourdes-men-s-graphic-t-shirt-lof1xh02ap-je130-113.html",
    DI.FOOTLOCKER: "https://www.footlocker.es/es/product/nike-tuned-3-hombre-zapatillas/314206809304.html"
}


class TestClass:
    def test_domains(self):
        pricelist.set_logger(logging.DEBUG)

        # Test fetching each page source in parallel
        def check_page_sources(url, drivers, sources, index):
            drivers[index] = fetch.chromedriver.webdriver_init()
            sources[index] = fetch.get_page_soup(url, driver=drivers[index])
            drivers[index].quit()

        # Test getting attributes from soup in parallel
        def check_data_from_soup(url, soup, results, index):
            results[index] = fetch.get_data_from_soup(url, soup)

        # Ensure all domains are being tested
        for d in [e for e in DI]:
            if d not in testURLs:
                logging.warning(f"{d.name} ({d.value}) not being tested, but exists in DomainInfo. Add a test URL to test it")

        urls_list = list(testURLs.values())
        drivers = [None] * len(urls_list)
        sources = [None] * len(urls_list)
        results = [None] * len(urls_list)

        # TODO Failed randomly, maybe race condition/threading issue?
        # Test URLs
        with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            for url in urls_list:
                executor.submit(check_page_sources, url, drivers, sources, urls_list.index(url))

        for src in sources:
            data = fetch.get_data_from_soup(url=urls_list[sources.index(src)], source=src)
            print(data)

        # TODO In parallel does not work (only some)
        # Test attributes from soup
        # with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
        #     for src in sources:
        #         executor.submit(check_data_from_soup, urls_list[sources.index(src)], src, results, sources.index(src))

        # if None in results:
        #     print(results)
        #     raise AssertionError("Some results are None")
        # for data in results:
        #     print(data)
