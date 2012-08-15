##
## Makefile (for developers)
##

package_name = awstatic
## WARNING: tmp_dir is deleted in the 'clean' rule. Be sure not to use
## "/tmp", "." or any directory that may contain anything else.
tmp_dir = /tmp/$(package_name)-distcheck
tmp_src_dir = $(tmp_dir)/src
tmp_cov_dir = $(tmp_dir)/coverage-output
tmp_env_dir = $(tmp_dir)/testing-env

.PHONY: _default
_default:
	@echo "make clean|cov|coverage|dist|distcheck|qa|sass|test"

.PHONY: clean
clean:
	rm -rf .coverage
	rm -rf ./dist/
	rm -rf $(tmp_dir)
	rm -rf .tox
	find . -name "__pycache__" | xargs rm -rf
	find . -name "*.pyc" | xargs rm

.PHONY: coverage
coverage:
	coverage run setup.py nosetests
	coverage html -d "$(tmp_cov_dir)"
	open "$(tmp_cov_dir)/index.html"
	@echo "Coverage information is available at '$(tmp_cov_dir)'."

cov: coverage

doc:
	cd docs && make html
	cd ..

.PHONY: dist
dist:
	python setup.py sdist

.PHONY: distcheck
distcheck: clean dist
	virtualenv --no-site-packages $(tmp_env_dir)
	$(tmp_env_dir)/bin/easy_install Nose
	$(tmp_env_dir)/bin/easy_install Coverage
	$(tmp_env_dir)/bin/easy_install readline
	mkdir -p $(tmp_src_dir)
	@name=`python setup.py --name` && \
		ver=`python setup.py --version` && \
		tar xfz ./dist/$$name-$$ver.tar.gz -C $(tmp_src_dir) && \
		cd $(tmp_src_dir)/$$name-$$ver && \
		$(tmp_env_dir)/bin/python setup.py install && \
		$(tmp_env_dir)/bin/nosetests

.PHONY:	qa
qa:
	pep8 -r --ignore=E121,E123,E127 setup.py || true
	pep8 -r --ignore=E121,E123,E127 $(package_name) || true
	pyflakes setup.py
	pyflakes $(package_name)

.PHONY: sass
sass:
	cd awstatic/template/assets/css && \
	    sass --watch src:. --style compressed

.PHONY: test
test:
	PYTHONWARNINGS=all nosetests && \
	    open awstatic/tests/js/tests.html