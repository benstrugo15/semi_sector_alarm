import pandas as pd
import requests
from typing import Union, Dict, List, Any
from src.conf.conf_loader import OPEN_AI_CONFIG
import json
import os


class GPTApi:
    def __init__(self, stocks_overview: List[Dict[str, str]], stocks_news, relevant_stocks_prices):
        self.stocks_overview = stocks_overview
        self.stocks_news = stocks_news
        self.relevant_stocks_prices = relevant_stocks_prices

    def gpt4_pipline(self):
        relevant_symbols_query = self.create_exploration_prompt(str(self.stocks_overview))
        stocks_semi_sectors = self.query_gpt4(relevant_symbols_query)
        relevant_semi_sectors = self.filter_single_sub_sectors(stocks_semi_sectors)
        relevant_semi_sectors_exploration = self.create_exploration_prompt2(str(relevant_semi_sectors))
        semi_sectors_data = self.query_gpt4(relevant_semi_sectors_exploration)
        all_relevant_stocks_data = self.merge_stocks_data(stocks_semi_sectors, semi_sectors_data)
        return all_relevant_stocks_data

    def query_gpt4(self, message_text):
        data = {
            "model": OPEN_AI_CONFIG.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that provides stock-related insights."
                }

                ,
                {"role": "user",
                  "content": message_text
                  }
            ]
            
        }
        headers = {"Content-Type": "application/json", "Authorization": os.getenv("OPENAI_TOKEN")}
        response = requests.post(OPEN_AI_CONFIG.URL, headers=headers, json=data)
        retry=3
        for i in range(retry):
            try:
                response_data = response.json()['choices'][0]['message']['content']
                start_index = response_data.find("[")
                end_index = response_data.rfind("]") + 1
                parse_data = json.loads(response_data[start_index: end_index])
                return parse_data
            except:
                print(response.text)
                if i ==retry-1:
                    raise response.text

    def merge_stocks_data(self, stocks_semi_sectors: List[Dict[str, str]], stocks_semi_sectors_exploration: List[Dict[str, str]]):
        organized_stocks_semi_sectors_exploration = pd.DataFrame(stocks_semi_sectors_exploration)
        organized_stocks_semi_sectors_exploration = organized_stocks_semi_sectors_exploration[organized_stocks_semi_sectors_exploration["is_core_focus_future_potential"] == True]
        organized_stocks_semi_sectors = pd.DataFrame(stocks_semi_sectors)
        organized_stocks_news = pd.DataFrame(self.stocks_news)
        organized_stocks_overview = pd.DataFrame(self.stocks_overview)
        all_relevant_data = organized_stocks_semi_sectors.merge(organized_stocks_semi_sectors_exploration, on="core_focus").\
            merge(organized_stocks_news, on="symbol", how="left").\
            merge(organized_stocks_overview, on="symbol").merge(self.relevant_stocks_prices, on="symbol").drop_duplicates()
        grouped = all_relevant_data.groupby('symbol').agg({
            'news_source': '***'.join,'news_data': '***'.join}).reset_index()
        other_columns = all_relevant_data.drop(['news_source', 'news_data'], axis=1).drop_duplicates()
        concat_data = pd.merge(grouped, other_columns, on='symbol', how='left')
        return concat_data.to_dict(orient="records")

    def filter_single_sub_sectors(self, stocks_semi_sectors: List[Dict[str, str]]):
        semi_sectors = pd.DataFrame(stocks_semi_sectors)
        semi_sectors["core_focus_count"] = semi_sectors.groupby("core_focus")["symbol"].transform('count')
        semi_sectors = semi_sectors[semi_sectors["core_focus_count"] > 1]
        core_focus = [{"core_focus": x} for x in semi_sectors["core_focus"].unique()]
        return core_focus


    @staticmethod
    def create_exploration_prompt(symbols: str):
        return f"""
                Provide the response in JSON format, with no ' character,
                i give you list of dicts, every dict have 2 keys: symbol, company_overview,
                the symbol is a stock symbol,
                and the company_overview is a company overview
                use the data i provide you, to add every dict, 1 more keys:
                "core_focus" and the value of the core_focus.
                the core_focus value will be "core focus of the company (symbol).
                for example: "quantum computing"
                if there are stocks symbols that have similar core_focus, give them the same core_focus value.
                for example: 
                if multiple company's core_focus is around "nuclear energy" or "nuclear power",
                give them the same core_focus value,
                but if multiple company's about energy, one about "solar energy" and one about "nuclear energy",
                they will have different core_focus.
                
                to make the response shorter, for every dict remove the "company_overview" key,
                and stay with those keys: symbol, core_focus.
                the data you need to work on: 

                {symbols}"""

    @staticmethod
    def create_exploration_prompt2(symbols: str):
        return f"""
                Provide the response in JSON format, with no ' character,
                i give you list of dicts, every dict have 1 key: 
                core_focus
                the core_focus is a primary business activities or industry sector for companies
                use the data i provide you, to add every dict, 3 more keys:
                "core_focus_overview" and the value of that - a core focus brief summary (not company, the core_focus),
                "is_core_focus_future_potential" and the value will be true if the core_focus 
                have the potential to significantly will change the future in the world in a large scale
                false if it is not,
                "core_focus_future_potential_overview": the value will be the reason it have 
                potential to significantly change the future in the world in a larger scale. 
            
                the data you need to work on: 
                
                {symbols}"""


if __name__ == '__main__':
    all_symbols_news2 = [{'news_data': 'Why Aspen Aerogels Shares Are Seeing Blue Skies On Wednesday',
                          'news_source': 'https://www.benzinga.com/news/earnings/24/10/41364884/why-aspen-aerogels-shares-are-seeing-blue-skies-on-wednesday',
                          'symbol': 'ASPN'}, {'news_data': 'Why I Keep Buying These 14 Incredible Growth Stocks',
                                              'news_source': 'https://www.fool.com/investing/2024/10/16/why-i-keep-buying-these-14-incredible-growth-stock/?source=iedfolrf0000001',
                                              'symbol': 'ASPN'}, {
                             'news_data': 'Thermal Management Materials and Systems Market Report 2025-2035: Analysis of Advanced Materials like Carbon Nanotubes, Graphene and Boron Nitride in Thermal Management',
                             'news_source': 'https://www.globenewswire.com/news-release/2024/10/11/2961838/28124/en/Thermal-Management-Materials-and-Systems-Market-Report-2025-2035-Analysis-of-Advanced-Materials-like-Carbon-Nanotubes-Graphene-and-Boron-Nitride-in-Thermal-Management.html',
                             'symbol': 'ASPN'}, {'news_data': 'Top 3 Cryptocurrency Stocks Poised for Major Gains',
                                                 'news_source': 'https://www.benzinga.com/markets/cryptocurrency/24/10/41357475/top-3-cryptocurrency-stocks-poised-for-major-gains',
                                                 'symbol': 'COIN'}, {
                             'news_data': 'Top 3 Cryptocurrency Stocks for Investors Seeking Double-Digit Upside Potential',
                             'news_source': 'https://www.investing.com/analysis/top-3-cryptocurrency-stocks-for-investors-seeking-doubledigit-upside-potential-200653054',
                             'symbol': 'COIN'}, {
                             'news_data': 'DEADLINE ALERT for COIN, NFE, DPZ: Law Offices of Howard G. Smith Reminds Investors of Class Actions on Behalf of Shareholders',
                             'news_source': 'https://www.globenewswire.com/news-release/2024/10/16/2964338/3448/en/DEADLINE-ALERT-for-COIN-NFE-DPZ-Law-Offices-of-Howard-G-Smith-Reminds-Investors-of-Class-Actions-on-Behalf-of-Shareholders.html',
                             'symbol': 'COIN'}, {'news_data': 'Why LanzaTech Shares Are Surging On Wednesday',
                                                 'news_source': 'https://www.benzinga.com/markets/equities/24/10/41364489/why-lanzatech-shares-are-surging-on-wednesday',
                                                 'symbol': 'LNZA'},
                         {'news_data': 'Top 3 Cryptocurrency Stocks Poised for Major Gains',
                          'news_source': 'https://www.benzinga.com/markets/cryptocurrency/24/10/41357475/top-3-cryptocurrency-stocks-poised-for-major-gains',
                          'symbol': 'CLSK'}, {
                             'news_data': 'Top 3 Cryptocurrency Stocks for Investors Seeking Double-Digit Upside Potential',
                             'news_source': 'https://www.investing.com/analysis/top-3-cryptocurrency-stocks-for-investors-seeking-doubledigit-upside-potential-200653054',
                             'symbol': 'CLSK'}, {
                             'news_data': "S&P 500 Extends Record Highs, Dow Breaks 43,000 Ahead Of Pivotal Earnings Week, Bitcoin's Rally Lifts Crypto Stocks: What's Driving Markets Monday?",
                             'news_source': 'https://www.benzinga.com/analyst-ratings/analyst-color/24/10/41319060/s-p-500-extends-record-highs-dow-breaks-43-000-ahead-of-pivotal-earnings-week-bitco',
                             'symbol': 'CLSK'},
                         {'news_data': 'Why SQM, Standard Lithium, and Piedmont Lithium Stocks All Dropped Today',
                          'news_source': 'https://www.fool.com/investing/2024/10/14/sqm-standard-lithium-piedmont-lithium-stocks-drop/?source=iedfolrf0000001',
                          'symbol': 'SLI'}, {'news_data': 'Why Standard Lithium Stock Is Still Going Up',
                                             'news_source': 'https://www.fool.com/investing/2024/10/10/why-standard-lithium-stock-is-still-going-up/?source=iedfolrf0000001',
                                             'symbol': 'SLI'}, {
                             'news_data': 'Why Arcadium Lithium Stock Exploded by 30% and Pulled Piedmont Lithium and Standard Lithium Higher Today',
                             'news_source': 'https://www.fool.com/investing/2024/10/09/arcadium-piedmont-standard-lithium-stocks-rise-30/?source=iedfolrf0000001',
                             'symbol': 'SLI'}, {
                             'news_data': '(Updated) NANO Nuclear Energy Reinforces its Nuclear Technology and Engineering Team Further with the Addition of Leading Researchers',
                             'news_source': 'https://www.globenewswire.com/news-release/2024/10/09/2960202/0/en/Updated-NANO-Nuclear-Energy-Reinforces-its-Nuclear-Technology-and-Engineering-Team-Further-with-the-Addition-of-Leading-Researchers.html',
                             'symbol': 'NNE'},
                         {'news_data': 'CVS Health: Are Its Three Divisions Better Off Apart Than Together?',
                          'news_source': 'https://www.investing.com/analysis/cvs-health-are-its-three-divisions-better-off-apart-than-together-200653052',
                          'symbol': 'WBA'}, {'news_data': 'Why Walgreens Boots Alliance Stock Is Skyrocketing Today',
                                             'news_source': 'https://www.fool.com/investing/2024/10/15/why-walgreens-boots-alliance-stock-is-skyrocketing/?source=iedfolrf0000001',
                                             'symbol': 'WBA'}, {
                             'news_data': 'Walgreens Boots Alliance Outlines Three-Cost Saving Strategy As Q4 Earnings Beat Street Estimates',
                             'news_source': 'https://www.benzinga.com/news/earnings/24/10/41333092/walgreens-boots-alliance-outlines-three-cost-saving-strategy-as-q4-earnings-beat-street-estimates',
                             'symbol': 'WBA'},
                         {'news_data': '3 Artificial Intelligence (AI) Stocks That Could Make You a Millionaire',
                          'news_source': 'https://www.fool.com/investing/2024/10/16/3-artificial-intelligence-ai-stocks-that-could-mak/?source=iedfolrf0000001',
                          'symbol': 'IONQ'},
                         {'news_data': 'Wall Street Analysts Think IonQ Is a Good Investment: Is It?',
                          'news_source': 'https://www.benzinga.com/news/earnings/24/10/41292829/wall-street-analysts-think-ionq-is-a-good-investment-is-it',
                          'symbol': 'IONQ'}, {'news_data': 'Why Wolfspeed Stock Blasted Higher (Again) Today',
                                              'news_source': 'https://www.fool.com/investing/2024/10/16/why-wolfspeed-stock-blasted-higher-again-today/?source=iedfolrf0000001',
                                              'symbol': 'WOLF'},
                         {'news_data': 'Why Wolfspeed Rocketed 20% Higher Today',
                          'news_source': 'https://www.fool.com/investing/2024/10/11/why-wolfspeed-rocketed-23-higher-today/?source=iedfolrf0000001',
                          'symbol': 'WOLF'}, {
                             'news_data': 'INVESTOR ALERT: Law Offices of Howard G. Smith Announces Investigation of Iris Energy Limited (IREN) on Behalf of Investors',
                             'news_source': 'https://www.benzinga.com/pressreleases/24/10/b41348857/investor-alert-law-offices-of-howard-g-smith-announces-investigation-of-iris-energy-limited-iren-o',
                             'symbol': 'IREN'}, {
                             'news_data': 'Glancy Prongay & Murray LLP, a Leading Securities Fraud Law Firm, Announces Investigation of Iris Energy Limited (IREN) on Behalf of Investors',
                             'news_source': 'https://www.benzinga.com/pressreleases/24/10/b41348689/glancy-prongay-murray-llp-a-leading-securities-fraud-law-firm-announces-investigation-of-iris-ener',
                             'symbol': 'IREN'}, {
                             'news_data': 'The Law Offices of Frank R. Cruz Announces Investigation of Iris Energy Limited (IREN) on Behalf of Investors',
                             'news_source': 'https://www.benzinga.com/pressreleases/24/10/b41346184/the-law-offices-of-frank-r-cruz-announces-investigation-of-iris-energy-limited-iren-on-behalf-of-i',
                             'symbol': 'IREN'}, {'news_data': 'Why NuScale Power Stock Was a Winner Today',
                                                 'news_source': 'https://www.fool.com/investing/2024/10/14/why-nuscale-power-stock-was-a-winner-today/?source=iedfolrf0000001',
                                                 'symbol': 'SMR'}, {'news_data': 'Is Cameco a Millionaire Maker?',
                                                                    'news_source': 'https://www.fool.com/investing/2024/10/14/is-cameco-a-millionaire-maker/?source=iedfolrf0000001',
                                                                    'symbol': 'SMR'},
                         {'news_data': 'Where Will NuScale Power Be in 5 Years?',
                          'news_source': 'https://www.fool.com/investing/2024/10/13/where-will-nuscale-power-be-in-5-years/?source=iedfolrf0000001',
                          'symbol': 'SMR'},
                         {'news_data': 'Why Trump Media & Technology Group Plummeted by Nearly 10% Today',
                          'news_source': 'https://www.fool.com/investing/2024/10/15/why-trump-media-technology-group-plummeted-by-near/?source=iedfolrf0000001',
                          'symbol': 'DJT'}, {'news_data': 'Why Trump Media Stock Was Soaring This Week',
                                             'news_source': 'https://www.fool.com/investing/2024/10/10/why-trump-media-stock-was-soaring-this-week/?source=iedfolrf0000001',
                                             'symbol': 'DJT'},
                         {'news_data': 'Why Trump Media Stock Is Making Big Gains Again Today',
                          'news_source': 'https://www.fool.com/investing/2024/10/10/why-trump-media-stock-is-making-big-gains-again-to/?source=iedfolrf0000001',
                          'symbol': 'DJT'}]
    all_symbols_summary2 = [{'symbol': 'ARQQ',
                             'company_overview': 'Arqit Quantum Inc is a cybersecurity company that has pioneered a\xa0symmetric key agreement technology that makes the communications links of any networked device or data at rest secure against current and future forms of cyber attack - even an attack from a quantum computer. The company delivers its symmetric key agreement technology via its product QuantumCloud. The firm operates in one segment that is, the provision of cybersecurity services via satellite and terrestrial platforms. The company operates and generates its revenue from UK.',
                             'marketCap': 439767247}, {'symbol': 'ASPN',
                                                       'company_overview': 'Aspen Aerogels Inc is an aerogel technology company that designs, develops, and manufactures high-performance aerogel insulation used in the energy industrial and sustainable insulation markets. The company also conducts research and development related to aerogel technology supported by funding from several agencies of the United States of America government and other institutions in the form of research and development contracts. It is engaged in two operating segment Energy Industrial and Thermal Barrier. Geographically, it operates in the U.S. and also has a presence in other International countries. It generates the majority of its revenue from the Energy Industrial segment and the United States market. Some of its products include Pyrogel XTE; Cryogel Z; Spaceloft Subsea; and others.',
                                                       'marketCap': 971439890}, {'symbol': 'OKLO',
                                                                                 'company_overview': 'Oklo Inc is developing advanced fission power plants to provide clean, reliable, and affordable energy at scale. It is pursuing two complementary tracks to address this demand: providing reliable, commercial-scale energy to customers; and selling used nuclear fuel recycling services to the U.S. market. The Company plans to commercialize its liquid metal fast reactor technology with the Aurora powerhouse product line. The first commercial Aurora powerhouse is designed to produce up to 15 megawatts of electricity (MWe) on both recycled nuclear fuel and fresh fuel.',
                                                                                 'marketCap': 3116214338},
                            {'symbol': 'CURV',
                             'company_overview': 'Torrid Holdings Inc is a direct-to-consumer brand of apparel, intimates, and accessories in North America targeting 27 to 42-year-old women. It is focused on fit and offers high-quality products across a broad assortment that includes tops, bottoms, denim, dresses, intimates, activewear, footwear, and accessories. The company has one reportable segment, which includes the operation of e-Commerce platform and stores.',
                             'marketCap': 541591477}, {'symbol': 'COIN',
                                                       'company_overview': 'Founded in 2012, Coinbase is the leading cryptocurrency exchange platform in the United States. The company intends to be the safe and regulation-compliant point of entry for retail investors and institutions into the cryptocurrency economy. Users can establish an account directly with the firm, instead of using an intermediary, and many choose to allow Coinbase to act as a custodian for their cryptocurrency, giving the company breadth beyond that of a traditional financial exchange. While the company still generates the majority of its revenue from transaction fees charged to its retail customers, Coinbase uses internal investment and acquisitions to expand into adjacent businesses, such as prime brokerage and data analytics.',
                                                       'marketCap': 62740549836}, {'symbol': 'GHRS',
                                                                                   'company_overview': 'GH Research PLC is a clinical-stage biopharmaceutical company dedicated to transforming the treatment of psychiatric and neurological disorders. The company is focused on developing novel and proprietary Mebufotenin 5-Methoxy-N, N-Dimethyltryptamine, or 5-MeO-DMT, therapies for the treatment of patients with Treatment-Resistant Depression, or TRD.',
                                                                                   'marketCap': 373041800},
                            {'symbol': 'DOGZ',
                             'company_overview': "Dogness (International) Corp designs, manufactures pet products, including leashes and smart products, and lanyards. The company designs, processes, and manufactures fashionable and high-quality leashes, collars, and harnesses to complement cats' and dogs' appearances, as well as intelligent pet products. The company also provides dyeing services to external customers, as well as pet grooming services. The dyeing service is to utilize the existing production capacity and the pet grooming service is immaterial. Geographically, it generates maximum revenue from Mainland China and also has a presence in the United States, Europe, Australia, Canada, Central, and South America, Japan, and other Asian countries and regions.",
                             'marketCap': 547036374}, {'symbol': 'CZFS',
                                                       'company_overview': 'Citizens Financial Services Inc is a Pennsylvania-chartered bank and trust company. The company through its banking subsidiary provides banking activities and services for individual, business, governmental and institutional customers. Its activities and services principally include checking, savings, and time deposit accounts; residential, commercial and agricultural real estate, commercial and industrial, state and political subdivision and consumer loans; and a variety of other specialized financial services. The Trust and Investment division of the Bank offers a full range of client investment, estate, mineral management and retirement services.',
                                                       'marketCap': 304908304}, {'symbol': 'ILLR',
                                                                                 'company_overview': 'Triller Group Inc is a us-based company that operates its businesses through Triller Corp which operates as a technology platform and AGBA Group Holding Limited operates as an insurance and wealth distribution platform.',
                                                                                 'marketCap': 411949314},
                            {'symbol': 'NUVB',
                             'company_overview': "Nuvation Bio Inc is a biopharmaceutical company tackling unmet needs in oncology by developing differentiated and novel therapeutic candidates. The company's clinical-stage product candidate is NUV-868, a BD2-selective oral small molecule BET inhibitor. NUV-868 inhibits the protein BRD4, a key member of the BET family that epigenetically regulates a number of important proteins that control tumor growth and differentiation, including oncogenes such as c-myc. Notably, BET proteins have critical biological functions and are found to be altered in many human cancers. It is also developing its proprietary, small molecule Drug-Drug Conjugate (DDC) platform, a novel therapeutic approach within the drug-conjugate class of anti-cancer therapies with parallels to Antibody-Drug Conjugates (ADCs).",
                             'marketCap': 893584124}, {'symbol': 'KRRO',
                                                       'company_overview': "Korro Bio Inc is a biopharmaceutical company with a mission to discover, develop, and commercialize a new class of genetic medicines based on editing RNA, enabling the treatment of both rare and highly prevalent diseases. It is generating a portfolio of differentiated programs that are designed to harness the body's natural RNA editing process to effect a precise yet transient single base edit. By editing RNA instead of DNA, Korro Bio is expanding the reach of genetic medicines by delivering additional precision and tunability.",
                                                       'marketCap': 363488566}, {'symbol': 'ASPI',
                                                                                 'company_overview': 'ASP Isotopes Inc is a pre-commercial stage advanced materials company dedicated to the development of technology and processes that, if successful, will allow for the production of isotopes that may be used in several industries. The company utilizes technology developed in South Africa over the past 20 years to enrich isotopes of elements or molecules with low atomic masses.',
                                                                                 'marketCap': 329108393},
                            {'symbol': 'RAPP',
                             'company_overview': 'Rapport Therapeutics Inc is a clinical-stage biopharmaceutical company focused on discovery and development of transformational small-molecule medicines for patients suffering from central nervous system disorders. Its foundational science has elucidated the complexities of neuronal receptor biology and enables the company to map and target certain neuronal receptor complexes. Neuronal receptors are complex assemblies of proteins, comprising receptor principal subunits and their receptor-associated proteins (RAPs), the latter of which play crucial roles in regulating receptor expression and function.',
                             'marketCap': 690563508}, {'symbol': 'RGTI',
                                                       'company_overview': "Rigetti Computing Inc is engaged in the business of full-stack quantum computing. Its proprietary quantum-classical infrastructure provides ultra-low latency integration with public and private clouds for high-performance practical quantum computing. The company has developed the industry's first multi-chip quantum processor for scalable quantum computing systems. Geographically, it derives a majority of its revenue from the United States.",
                                                       'marketCap': 4783243906}, {'symbol': 'LEU',
                                                                                  'company_overview': "Centrus Energy Corp is engaged in the supply of nuclear fuel and services for the nuclear power industry. It operates through the Low-Enriched Uranium (LEU) and Technical Solutions segments. The LEU segment has two components which include the sale of separative work units and uranium. The Technical Solutions segment provides\xa0engineering, design, and manufacturing services to government and private sector customers. The majority of the firm's revenue is derived from the LEU segment. It has a business presence in the U.S. and other countries, of which prime revenue is generated in the U.S.",
                                                                                  'marketCap': 1139715432},
                            {'symbol': 'AMPS',
                             'company_overview': 'Altus Power Inc is a developer, owner, and operator of large-scale photovoltaic and energy storage systems across the United States. The company serve commercial, industrial, public sector, and community solar customers. Its mission is to drive the clean energy transition by developing and operating solar generation and energy storage facilities. It owns a diverse portfolio of solar PV systems and has long-term agreements with enterprise entities and residential customers. Their primary product offerings include leases and revenue contracts for solar power generation, alongside electric vehicle charging and energy storage solutions. Revenue streams include power purchase agreements, net metering credit agreements, and SREC revenue.',
                             'marketCap': 655998061}, {'symbol': 'PLRX',
                                                       'company_overview': 'Pliant Therapeutics Inc is a clinical-stage biopharmaceutical company focused on discovering and developing novel therapies for the treatment of fibrosis and related diseases. Its primary\xa0product candidate is bexotegrast (PLN-74809), an oral, small molecule, that the company is developing for the treatment of idiopathic pulmonary fibrosis, or IPF, and primary sclerosing cholangitis.',
                                                       'marketCap': 782881860}, {'symbol': 'LNZA',
                                                                                 'company_overview': "LanzaTech Global Inc is a nature-based carbon refining company that transforms waste carbon into the chemical building blocks for consumer goods such as sustainable fuels, fabrics, and packaging that people use in their daily lives. The company's goal is to reduce the need for virgin fossil fuels by challenging and striving to change the way the world uses carbon.",
                                                                                 'marketCap': 365916580}
                            ]
    repetative_upside_stocks2 = [{'symbol': 'ABLVW', 'last_price': 0.0191, 'last_percent': 43.60902255639098,
                                  'start_end_percent': 27.333333333333332},
                                 {'symbol': 'ABLVW', 'last_price': 0.0191, 'last_percent': 43.60902255639098,
                                  'start_end_percent': 27.333333333333332},
                                 {'symbol': 'ADCT', 'last_price': 3.22, 'last_percent': 6.976744186046524,
                                  'start_end_percent': 12.195121951219514},
                                 {'symbol': 'ADSEW', 'last_price': 3.25, 'last_percent': 19.926199261992615,
                                  'start_end_percent': 21.2686567164179},
                                 {'symbol': 'ADVWW', 'last_price': 0.0339, 'last_percent': 9.354838709677416,
                                  'start_end_percent': 21.94244604316547},
                                 {'symbol': 'ADVWW', 'last_price': 0.0339, 'last_percent': 9.354838709677416,
                                  'start_end_percent': 21.94244604316547},
                                 {'symbol': 'AEVA-WT', 'last_price': 0.046, 'last_percent': 14.143920595533487,
                                  'start_end_percent': -6.122448979591842},
                                 {'symbol': 'AILEW', 'last_price': 0.2701, 'last_percent': 12.541666666666673,
                                  'start_end_percent': 28.00947867298579},
                                 {'symbol': 'AILEW', 'last_price': 0.2701, 'last_percent': 12.541666666666673,
                                  'start_end_percent': 28.00947867298579},
                                 {'symbol': 'ALAR', 'last_price': 16.64, 'last_percent': 33.11999999999999,
                                  'start_end_percent': 73.69519832985387},
                                 {'symbol': 'ALAR', 'last_price': 16.64, 'last_percent': 33.11999999999999,
                                  'start_end_percent': 73.69519832985387},
                                 {'symbol': 'ALTS', 'last_price': 2.26, 'last_percent': 5.607476635513997,
                                  'start_end_percent': 32.16374269005847},
                                 {'symbol': 'AMBP-WT', 'last_price': 0.05, 'last_percent': 19.047619047619047,
                                  'start_end_percent': 38.88888888888891},
                                 {'symbol': 'AMBP-WT', 'last_price': 0.05, 'last_percent': 19.047619047619047,
                                  'start_end_percent': 38.88888888888891},
                                 {'symbol': 'AMPS', 'last_price': 3.76, 'last_percent': 24.50331125827814,
                                  'start_end_percent': 24.09240924092409},
                                 {'symbol': 'AMSC', 'last_price': 26.39, 'last_percent': 13.407821229050288,
                                  'start_end_percent': 11.256323777403043},
                                 {'symbol': 'ANVS', 'last_price': 9.14, 'last_percent': 14.536340852130337,
                                  'start_end_percent': 13.540372670807452},
                                 {'symbol': 'APLD', 'last_price': 8.05, 'last_percent': 10.273972602739745,
                                  'start_end_percent': 8.783783783783788},
                                 {'symbol': 'APRE', 'last_price': 3.5, 'last_percent': 14.754098360655753,
                                  'start_end_percent': 36.71874999999999},
                                 {'symbol': 'APRE', 'last_price': 3.5, 'last_percent': 14.754098360655753,
                                  'start_end_percent': 36.71874999999999},
                                 {'symbol': 'AREB', 'last_price': 2.88, 'last_percent': 9.090909090909083,
                                  'start_end_percent': 21.518987341772142},
                                 {'symbol': 'ARQQ', 'last_price': 6.76, 'last_percent': 39.95859213250517,
                                  'start_end_percent': 75.58441558441558},
                                 {'symbol': 'ARQQ', 'last_price': 6.76, 'last_percent': 39.95859213250517,
                                  'start_end_percent': 75.58441558441558},
                                 {'symbol': 'ASPI', 'last_price': 3.5, 'last_percent': 20.68965517241379,
                                  'start_end_percent': 22.807017543859644},
                                 {'symbol': 'ASPN', 'last_price': 25.41, 'last_percent': 13.235294117647056,
                                  'start_end_percent': 11.938325991189432},
                                 {'symbol': 'ATNF', 'last_price': 6.47, 'last_percent': 325.65789473684214,
                                  'start_end_percent': 372.2627737226277},
                                 {'symbol': 'ATNF', 'last_price': 6.47, 'last_percent': 325.65789473684214,
                                  'start_end_percent': 372.2627737226277},
                                 {'symbol': 'ATNFW', 'last_price': 0.0177, 'last_percent': 113.25301204819276,
                                  'start_end_percent': 94.5054945054945},
                                 {'symbol': 'ATNFW', 'last_price': 0.0177, 'last_percent': 113.25301204819276,
                                  'start_end_percent': 94.5054945054945},
                                 {'symbol': 'ATOM', 'last_price': 3.62, 'last_percent': 5.84795321637428,
                                  'start_end_percent': 12.074303405572758},
                                 {'symbol': 'AUID', 'last_price': 7.75, 'last_percent': 19.59876543209875,
                                  'start_end_percent': 27.887788778877898},
                                 {'symbol': 'AUROW', 'last_price': 0.945, 'last_percent': 11.176470588235299,
                                  'start_end_percent': 24.342105263157887},
                                 {'symbol': 'AVTX', 'last_price': 10.29, 'last_percent': 6.19195046439629,
                                  'start_end_percent': 13.953488372093023},
                                 {'symbol': 'AZ', 'last_price': 3.75, 'last_percent': 25.41806020066888,
                                  'start_end_percent': 87.5},
                                 {'symbol': 'AZ', 'last_price': 3.75, 'last_percent': 25.41806020066888,
                                  'start_end_percent': 87.5},
                                 {'symbol': 'BDRX', 'last_price': 8.4, 'last_percent': 67.66467065868265,
                                  'start_end_percent': 75.36534446764092},
                                 {'symbol': 'BGXX', 'last_price': 0.195, 'last_percent': 8.635097493036215,
                                  'start_end_percent': 94.80519480519483},
                                 {'symbol': 'BGXX', 'last_price': 0.195, 'last_percent': 8.635097493036215,
                                  'start_end_percent': 94.80519480519483},
                                 {'symbol': 'BIAF', 'last_price': 2.18, 'last_percent': 10.1010101010101,
                                  'start_end_percent': 9.547738693467345},
                                 {'symbol': 'BMTX-WT', 'last_price': 0.0499, 'last_percent': 19.377990430622027,
                                  'start_end_percent': 66.33333333333334},
                                 {'symbol': 'BMTX-WT', 'last_price': 0.0499, 'last_percent': 19.377990430622027,
                                  'start_end_percent': 66.33333333333334},
                                 {'symbol': 'BNAIW', 'last_price': 0.0393, 'last_percent': 6.216216216216219,
                                  'start_end_percent': 11.64772727272727},
                                 {'symbol': 'BQ', 'last_price': 0.608, 'last_percent': 12.592592592592577,
                                  'start_end_percent': 17.14836223506743},
                                 {'symbol': 'BQ', 'last_price': 0.608, 'last_percent': 12.592592592592577,
                                  'start_end_percent': 17.14836223506743},
                                 {'symbol': 'BSLK', 'last_price': 0.562, 'last_percent': 14.693877551020428,
                                  'start_end_percent': 12.400000000000011},
                                 {'symbol': 'BTDR', 'last_price': 8.35, 'last_percent': 7.4646074646074645,
                                  'start_end_percent': 23.338257016248157},
                                 {'symbol': 'CBUS', 'last_price': 3.7, 'last_percent': 5.113636363636376,
                                  'start_end_percent': 25.850340136054427},
                                 {'symbol': 'CCCC', 'last_price': 7.0, 'last_percent': 11.111111111111116,
                                  'start_end_percent': 38.339920948616616},
                                 {'symbol': 'CDIOW', 'last_price': 0.0423, 'last_percent': 28.96341463414631,
                                  'start_end_percent': 20.857142857142836},
                                 {'symbol': 'CDIOW', 'last_price': 0.0423, 'last_percent': 28.96341463414631,
                                  'start_end_percent': 20.857142857142836},
                                 {'symbol': 'CDIOW', 'last_price': 0.0423, 'last_percent': 28.96341463414631,
                                  'start_end_percent': 20.857142857142836},
                                 {'symbol': 'CDT', 'last_price': 0.1144, 'last_percent': 11.392405063291132,
                                  'start_end_percent': 3.9055404178019963},
                                 {'symbol': 'CDT', 'last_price': 0.1144, 'last_percent': 11.392405063291132,
                                  'start_end_percent': 3.9055404178019963},
                                 {'symbol': 'CGBS', 'last_price': 0.28, 'last_percent': 6.10079575596818,
                                  'start_end_percent': 3.703703703703707},
                                 {'symbol': 'CHNR', 'last_price': 0.7491, 'last_percent': 7.320916905444141,
                                  'start_end_percent': -0.7288629737609409},
                                 {'symbol': 'CHRO', 'last_price': 0.891, 'last_percent': 22.222222222222232,
                                  'start_end_percent': 41.65341812400636},
                                 {'symbol': 'CHRO', 'last_price': 0.891, 'last_percent': 22.222222222222232,
                                  'start_end_percent': 41.65341812400636},
                                 {'symbol': 'CHRO', 'last_price': 0.891, 'last_percent': 22.222222222222232,
                                  'start_end_percent': 41.65341812400636},
                                 {'symbol': 'CIFR', 'last_price': 5.01, 'last_percent': 14.383561643835607,
                                  'start_end_percent': 32.89124668435013},
                                 {'symbol': 'CIFR', 'last_price': 5.01, 'last_percent': 14.383561643835607,
                                  'start_end_percent': 32.89124668435013},
                                 {'symbol': 'CIFRW', 'last_price': 1.45, 'last_percent': 9.84848484848484,
                                  'start_end_percent': 31.818181818181802},
                                 {'symbol': 'CLSK', 'last_price': 11.84, 'last_percent': 5.431878895814779,
                                  'start_end_percent': 33.63431151241535},
                                 {'symbol': 'CLSK', 'last_price': 11.84, 'last_percent': 5.431878895814779,
                                  'start_end_percent': 33.63431151241535},
                                 {'symbol': 'CNEY', 'last_price': 0.6634, 'last_percent': 10.419440745672425,
                                  'start_end_percent': 25.9301442672741},
                                 {'symbol': 'CNEY', 'last_price': 0.6634, 'last_percent': 10.419440745672425,
                                  'start_end_percent': 25.9301442672741},
                                 {'symbol': 'CNTX', 'last_price': 2.05, 'last_percent': 5.128205128205132,
                                  'start_end_percent': 11.413043478260855},
                                 {'symbol': 'CNVS', 'last_price': 1.78, 'last_percent': 20.6779661016949,
                                  'start_end_percent': 20.270270270270274},
                                 {'symbol': 'COIN', 'last_price': 210.48, 'last_percent': 7.201792808393592,
                                  'start_end_percent': 26.05857339641851},
                                 {'symbol': 'CONL', 'last_price': 33.33, 'last_percent': 14.261227288309897,
                                  'start_end_percent': 54.95118549511852},
                                 {'symbol': 'CONL', 'last_price': 33.33, 'last_percent': 14.261227288309897,
                                  'start_end_percent': 54.95118549511852},
                                 {'symbol': 'CONL', 'last_price': 33.33, 'last_percent': 14.261227288309897,
                                  'start_end_percent': 54.95118549511852},
                                 {'symbol': 'CPTNW', 'last_price': 0.0118, 'last_percent': 14.563106796116498,
                                  'start_end_percent': 28.26086956521739},
                                 {'symbol': 'CPTNW', 'last_price': 0.0118, 'last_percent': 14.563106796116498,
                                  'start_end_percent': 28.26086956521739},
                                 {'symbol': 'CREVW', 'last_price': 0.0348, 'last_percent': 9.090909090909083,
                                  'start_end_percent': -10.769230769230775},
                                 {'symbol': 'CRPT', 'last_price': 14.39, 'last_percent': 5.113221329437545,
                                  'start_end_percent': 16.896831844029244},
                                 {'symbol': 'CSSEQ', 'last_price': 0.008, 'last_percent': 14.28571428571428,
                                  'start_end_percent': -20.0},
                                 {'symbol': 'CSSEQ', 'last_price': 0.008, 'last_percent': 14.28571428571428,
                                  'start_end_percent': -20.0},
                                 {'symbol': 'CTXR', 'last_price': 0.412, 'last_percent': 10.130981021117336,
                                  'start_end_percent': 5.048444671086177},
                                 {'symbol': 'CURI', 'last_price': 2.57, 'last_percent': 13.716814159292046,
                                  'start_end_percent': 37.433155080213886},
                                 {'symbol': 'CURI', 'last_price': 2.57, 'last_percent': 13.716814159292046,
                                  'start_end_percent': 37.433155080213886},
                                 {'symbol': 'CURR', 'last_price': 2.53, 'last_percent': 14.479638009049767,
                                  'start_end_percent': 24.630541871921185},
                                 {'symbol': 'CURV', 'last_price': 3.83, 'last_percent': 5.8011049723756924,
                                  'start_end_percent': 12.647058823529417},
                                 {'symbol': 'CVKD', 'last_price': 15.35, 'last_percent': 5.862068965517242,
                                  'start_end_percent': 28.451882845188287},
                                 {'symbol': 'CYN', 'last_price': 4.19, 'last_percent': 6.345177664974622,
                                  'start_end_percent': 13.24324324324325},
                                 {'symbol': 'CZFS', 'last_price': 62.36, 'last_percent': 5.1424717585567326,
                                  'start_end_percent': 14.191540010987},
                                 {'symbol': 'DBGIW', 'last_price': 14.0, 'last_percent': 12.00000000000001,
                                  'start_end_percent': 33.33333333333333},
                                 {'symbol': 'DBGIW', 'last_price': 14.0, 'last_percent': 12.00000000000001,
                                  'start_end_percent': 33.33333333333333},
                                 {'symbol': 'DBGIW', 'last_price': 14.0, 'last_percent': 12.00000000000001,
                                  'start_end_percent': 33.33333333333333},
                                 {'symbol': 'DFLI', 'last_price': 0.622, 'last_percent': 11.270125223613592,
                                  'start_end_percent': 13.91941391941391},
                                 {'symbol': 'DGHI', 'last_price': 1.2605, 'last_percent': 17.803738317756988,
                                  'start_end_percent': 25.422885572139315},
                                 {'symbol': 'DJT', 'last_price': 31.26, 'last_percent': 15.521064301552112,
                                  'start_end_percent': 51.968886728245025},
                                 {'symbol': 'DJT', 'last_price': 31.26, 'last_percent': 15.521064301552112,
                                  'start_end_percent': 51.968886728245025},
                                 {'symbol': 'DJT', 'last_price': 31.26, 'last_percent': 15.521064301552112,
                                  'start_end_percent': 51.968886728245025},
                                 {'symbol': 'DJTWW', 'last_price': 23.125, 'last_percent': 13.748155435317265,
                                  'start_end_percent': 67.8156748911466},
                                 {'symbol': 'DJTWW', 'last_price': 23.125, 'last_percent': 13.748155435317265,
                                  'start_end_percent': 67.8156748911466},
                                 {'symbol': 'DJTWW', 'last_price': 23.125, 'last_percent': 13.748155435317265,
                                  'start_end_percent': 67.8156748911466},
                                 {'symbol': 'DLPN', 'last_price': 1.45, 'last_percent': 98.63013698630137,
                                  'start_end_percent': 113.23529411764703},
                                 {'symbol': 'DLPN', 'last_price': 1.45, 'last_percent': 98.63013698630137,
                                  'start_end_percent': 113.23529411764703},
                                 {'symbol': 'DOGZ', 'last_price': 40.57, 'last_percent': 5.212655601659755,
                                  'start_end_percent': 10.695770804911328}]
    a = GPTApi(all_symbols_summary2, all_symbols_news2, repetative_upside_stocks2)
    b = a.gpt4_pipline()
    c = b
