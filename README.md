<<<<<<< HEAD
# Verkehrsdetektion-berlin

## Dataset - Verkehrsdetektion Berlin
> The dataset is described in german.
> If required, use a translator/llm of your choice.

[govdata.de](https://www.govdata.de/suche/daten/verkehrsdetektion-berlin)

[viz.berlin.de](https://api.viz.berlin.de/daten/verkehrsdetektion)

The dataset format is described in the [readme.txt](https://mdhopendata.blob.core.windows.net/verkehrsdetektion/readme.txt) file.

> Currently, there is ongoing work to re-structurize the dataset. Be careful and always double check, if the actual dataformat matches the description and is plausible. The data is available in two formats: `alte_qualitaetssicherung` and `neue_qualitaetssicherung`.
We will only use `alte_qualitaetssicherung`.

There are `Fahrstreifendetektoren` which measure the vehicles for a individual lane.
We will work with the `Messquerschnitt`-data, which are the aggregated data for all `Fahrstreifendetektoren` of a street that have the same driving direction.
In the following, I will abbreviate `Messquerschnitt` as `MQ`.

## getting started
Set up a virtual environment!
If you have no idea how, you can do it like this:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Once installed you can always activate the environment like this: `source .venv/bin/activate`.
You can install additional packages with `pip install jupyter`.

To deactivate the environment you can simply type: `deactivate`.

### downloading data
```bash
python3 get_data.py
```
The data is downloaded into the `data/` directory, where `csv/` contains the unpacked .csv files.

### using the data
In `main.py`, you can find code to load the data into a single pandas `DataFrame` and create two simple plots.

Run it like this: `python3 main.py` and inspect the plots in the `out/` directory.


## Mandatory Tasks
0. Make yourself familiar with the structure of the dataset.
1. Where are the individual `MQ`'s located and when were they set up? Are all of them still in operation? Identify the year with the best data coverage and answer question 2&3 only for this single year.
2. Analyze the daily patterns of cars (e.g. heatmaps). Identify anomalies and traffic peaks.
3. Can you figure out the speed limit at each `MQ`? Is there a connection between speed limit, maximum traffic peak and lane number? (You may use other datasets to answer this.) 

=======
# Programming_Starter



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://git.oth-aw.de/6e6e/programming_starter.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://git.oth-aw.de/6e6e/programming_starter/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
>>>>>>> e7afd6fe9d522e62d3e231b6f97b4f53b3a66898
# berlin-traffic
