# H1 EGM722_Assignment

## H2 Coding Assignment for EGM722: Programming for GIS and Remote Sensing at Ulster University
 
**Setup and Installation**

1. Firstly it is important to ensure that your computer operating system is compatible with Git version control and Conda package and environment management system.  Windows was used for this project and the code was developed through GitHub Desktop and Anaconda Navigator.  If Git has not already been installed, this can be done by downloading the latest Git for Windows installer from git-scm.com.  To use Conda, download and install Anaconda Navigator from anaconda.com.

2. The next step is to access the project’s environment.yml file, included in the above repository, from within the Anaconda Navigator desktop software.  This ensures that the code is reproducible by importing the same Python packages and dependencies that were used to run the script.  From the Anaconda homepage, select the “Environments” tab, then then “Import” button, then navigate to and open the environment.yml file.  The content of this file is limited to a list of the main packages used to run both scripts.
The Part A and Part B scripts are provided as Python documents in the repository, identifiable by .py extensions.  These scripts were written in PyCharm.  For ease of use it is recommended to download this or another IDE to run the code.

3. Both scripts have been developed with specific test data, acquired from the Recent Decisions section of the Planning Appeals Commission website (https://appeals.pacni.gov.uk/OnlineSearch/AppealsDecision) and geocoded in ArcPro.  This information was manually scraped from successive PAC webpages and added to a spreadsheet containing data of the same parameters taken from the same source for a similar project one year previously.

4. PAC publishes its decisions from the last six months on a rolling basis, which introduced a time limitation element in gathering data from the website.  However, the script is flexible and the CSV file can be updated with either dummy data or new appeal decisions as they are published.  For each location identified by XY coordinates, the script only requires an appeal outcome and appeal reference number.

5. All other data was deemed unnecessary for this project and was removed from the CSV file using a GitHub development branch, including appellant names, addresses and other published information.

6. The other required data files are shapefiles of the Northern Ireland outline, LGD boundaries and water bodies.  These are available to download from the Open Data NI website by accessing the following links:
	o	https://www.opendatani.gov.uk/dataset/osni-open-data-largescale-boundaries-ni-outline  (Northern Ireland outline)
	o	https://www.opendatani.gov.uk/dataset/osni-open-data-largescale-boundaries-local-government-districts-2012  (LGD boundaries)
	o	https://www.opendatani.gov.uk/dataset/lakes-of-northern-ireland (water bodies).

