Dependencies :

apt-get install python-tz


To run dao tests

- Install postgres sql
- Create a database asterisktest
- Create a user asterisk / passwd asterisk
        create DATABASE asterisktest;
        create USER asterisk with password 'asterisk';
        grant all ON DATABASE asterisktest to asterisk;