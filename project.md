**Projekt célja**
Pump.fun tokenek megjelenítése informatív web base footprint charton 


**Technologia stack**
python
websocket
tailwind
vue3
vite (a fejlesztéshez)

**Megvalósítás leírása**
A footprint.example.py file tartalmaz egy offline változatot amely szimpla html generáláson alapszik.
Ennek az online változatát kell megoldani backend-frontend formában.

Az adatok websocketen érkeznek a pumpapi websocketen. Jelenleg a pumpapi csak egy websocketet enged ezért van egy 
lokális feeder amit hasznaálni tudunk. ws://192.168.1.122:9944 Erre kell csatlakozni. A protokoll és az adatok 100%-ban
megegegyeznek a pumpapi-val.

A bejövő adatokat kétféle bucketbe kell aggregálni. 1sec és 10sec
Az 1 sec-es bucketek csak indikátorok számolására használjuk. pl RSI14 
A 10sec -es bucketekből készítünk footprint chartot. 

Egy token akkor válik aktívvá (innentől trackeljük) mikor migrálódik. (migrate event: pumpapi.io_stream_docs.md)
A migrálástól számítva 10 percig aktív. Utána már nem érdekel, eldobjuk.
Tehát 10 percen keresztül kell trackelni.

A felületen felül jelenjenek meg az éppen aktív tokenek soronként.
- <mint address> kattintható link, új lapon nyitja a gmgn oldalát: https://gmgn.ai/sol/token/<mint>
- Mellette egy kis ikon amivel ki tudom copy-zni a mind address-t
- Mióta aktív (sec) (9. percben már legyen piros, közeleg a vége)
- Trade per 10sec
- Marketcap USD-ben - a SOL értékét konstansban adom meg, jelenleg 85 dollár
- 1sec -es RSI értéke, színezve 0-30-70-100 piros - zöld

A kiválasztott tokenről kell footprint chartot készíteni. A következőképpen:

Készíts vue-ban adat modellt. Az x tengely fix mert 10 percig követjük a tokent és 10sec a bucket, tehát 60 telemű a modell.
Az y tengelyen 1k marketcapenként legyenek a klaszterek. Ez dinamikusan bővül ahogy épül fel a footprint chart.
Kb 35k marketcapnél migrálódik a token. Az indulási szélesség legyen 20k -tól 50k-ig, tehát az induló adatmodell 30 elemű lesz.
Ha 50k fölé vagy 20k alá megy a token akkor bővül.

A design többi része a footprint.example.py -ben van, a borderrel készítjük el a gyertyákat. A buy-sell pedig a klaszterek belsejében.

Az alső statisztikai bar a footprint.example.py -nak megfelelően legyen. Ezt bővíteni fogjuk!

Ha kiválasztok egy tokent akkor azt a listában jelezze úgy, hogy a háttér más színű lesz.

A végső production apphoz ne kelljen külső webszerver. A python szolgálja ki a buildelt frontendet.