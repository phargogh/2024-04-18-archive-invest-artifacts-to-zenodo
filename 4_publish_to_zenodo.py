import textwrap

import requests

# This is the content we would normally expect to receive from the .zenodo.json
# file in the repo.
ZENODO_JSON = {
    "creators": [
        {
            "name": "The Natural Capital Project",
        }
    ],
    "upload_type": "software",
    "publication_date": "2008-07-07",  # Initial InVEST release
    "title": "InVEST: Integrated Valuation of Ecosystem Services and Tradeoffs",
    "description": textwrap.dedent(
        """\
        InVEST® is a suite of free, open-source software models used to map and
        value the goods and services from nature that sustain and fulfill human
        life.  If properly managed, ecosystems yield a flow of services that
        are vital to humanity, including the production of goods (e.g., food),
        life-support processes (e.g., water purification), and life-fulfilling
        conditions (e.g., beauty, opportunities for recreation), and the
        conservation of options (e.g., genetic diversity for future use).
        Despite its importance, this natural capital is poorly understood,
        scarcely monitored, and, in many cases, undergoing rapid degradation
        and depletion.

        Governments, non-profits, international lending institutions, and
        corporations all manage natural resources for multiple uses and
        inevitably must evaluate tradeoffs among them. The multi-service,
        modular design of InVEST provides an effective tool for balancing the
        environmental and economic goals of these diverse entities.

        InVEST enables decision makers to assess quantified tradeoffs
        associated with alternative management choices and to identify areas
        where investment in natural capital can enhance human development and
        conservation.  The toolset includes distinct ecosystem service models
        designed for terrestrial, freshwater, marine, and coastal ecosystems,
        as well as a number of “helper tools” to assist with locating and
        processing input data and with understanding and visualizing outputs.
        """),
    "access_right": "open",
    "license": None,  # 3-clause BSD, else apache2
    "prereserve_doi": True,
    "keywords": ["Ecosystem Services", "Geospatial", "Models"],
    # "contributors"  # not required, but would be nice to include
    "communities": [{"identifier": "natcap"}],
    # "grants"  # not required, could be interesting to include since we have
    # lots of grants supporting InVEST
    "version": None,
    "language": "en",
}

# Is the above metadata only required for the initial deposition or also when
# creating a new version?  NO, new versions also have all deposition
# attributes.
#
# ALSO: We cannot add all new versions and _then_ publish, we must create a
# new version and then publish it before creating the next version.
