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
        def check_page_sources(drivers, sources, dom):
            drivers[dom] = fetch.chromedriver.webdriver_init()
            sources[dom] = fetch.get_page_soup(testURLs[dom], driver=drivers[dom])

        # Test getting attributes from soup in parallel
        def check_data_from_soup(sources, results, dom):
            results[dom] = fetch.get_data_from_soup(testURLs[dom], sources[dom])

        # Fallback if source is None
        def source_fallback(sources):
            for dom, src in sources.items():
                if src is None:
                    sources[dom] = fetch.get_page_soup(testURLs[dom])
            sources[DI.ELCORTEINGLES] = None
            if None in sources:
                raise AssertionError("Some page sources are None")
            return sources

        # Fallback if result is None
        def result_fallback(results, sources):
            for dom, res in results.items():
                if res is None:
                    results[dom] = fetch.get_data_from_soup(testURLs[dom], sources[dom])
            if None in results:
                raise AssertionError("Some results are None")
            return results

        # Ensure all domains are being tested
        for d in [e for e in DI]:
            if d not in testURLs:
                print(f"\n{d.name} ({d.value}) not being tested, but exists in DomainInfo. Add a test URL to test it.")

        drivers = {e: None for e in testURLs}
        sources = {e: None for e in testURLs}
        results = {e: None for e in testURLs}

        # Test URLs
        with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            for dom in testURLs:
                executor.submit(check_page_sources, drivers, sources, dom)

        if None in sources.values():
            logging.error("Some sources are None. Trying single thread fallback.")
            sources = source_fallback(sources)

        # Test attributes from soup
        with ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            for dom in sources:
                executor.submit(check_data_from_soup, sources, results, dom)

        if None in results.values():
            logging.error("Some results are None. Trying single thread fallback...")
            results = result_fallback(results, sources)

        for data in results.values():
            print(data)
