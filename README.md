# Создал бота с помощью BotFather (получаем токен для его работы)
Затем из интернета нашёл, что использование WebHook при локальном запуске невозможно (по причине того, что локальный адрес является серым по умолчанию), по этой причине был выбран путь (единственный возможный) использования getUpdates, который возвращает последние (максимум 100) обновлений (в данном случае сообщений), среди которых за счёт их id мы выбираем новые. Для того, чтобы получать всегда последние сообщений происходит взятие последних 10-и сообщений.
После написания базового функционала бота и сериализации/десериализации данных требовалось связать бота с ВК.
Так как основным функционалом является отправка сообщений в ВК, то сначала я изучил ВК АПИ, но, узнав, что с 2019-го года они запретили отправку сообщений от пользователя (доступно только для сообществ) я решил воспользоваться функционалом /dev/, который используется на сайте вк апи для демонстрации методов. Мною был написан метод авторизации, когда я наткнулся на статью на хабре (https://habr.com/ru/post/319178/), в которой был дан код аналогичный моему, но более высокого качества и содержащий обработку исключений (из за того, что основным массивом кода являются headers, я решил использовать его как библиотеку взамен библиотеки ВК АПИ, для чего вынес его в отделбный файл messages.py, из которого импортирую классы), но не смотря на качество кода его пришлось дработать (у него было неверно написано регулярное выражение).
Затем, написав более удобный пользовательский интерфейс, я закончил работу.

Весь использованный функционал можно найти в imports