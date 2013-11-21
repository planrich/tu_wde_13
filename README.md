
README
===========

In this exercise we chose to wrap different restaurant finder webapplications
and combine their results into a single XML additionally displaying it later in
an html file.

We used WebL to extract www.mjam.net and open.dapper.net for www.just-eat.co.uk.
to start the extraction one can issue the following command:

python3 query.py 1090,M40 Pizza

to get all restaurants in the 9. Bezirk that offer pizza and also all restaurants
that offer pizza in the M40 district in Manchester UK.

The filtering option is very limited in just-eat webapp as they only allow a
very limited set of search queries.

An image is included (wde_grp7A_1_arch.png) which describes the steps executed
to extract the data, merge them and open up a browser.

1. For each zipcode the corrisponding XML from the corresponding website is loaded (either mjam.at or just-eat.co.uk)
2. That is the parsed using pythons xml dom parser (etree) and data is cleaned and
   merged together
3. data is saved into a temporary file and a browser tab is opened to display
   the results

As dapper cannot be included so easily we have provided screenshots of the
configuration named as dapper_step_?.zip
