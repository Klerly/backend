# run django tests and exit with a non-zero exit code if any tests fail
# Usage: ./test.sh

# run the tests
python3 manage.py test --settings=Klerly.settings.test --parallel
if [ $? -ne 0 ]; then
    exit 1
fi
