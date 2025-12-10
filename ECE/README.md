# IndySCC25-ClimateEmulator

For the Exascale Climate Emulator **code**, please use the upstream repo:
- For Task 1:  <https://github.com/ecrc/exageostatcpp>.
- For Task 2: <https://github.com/ecrc/hicma-x> (Alternatively, hicma-x is also available as branch `climate_emulator` of this repository).

The default branch (SC25) of this repo has the task instructions and related information, in a file named `IndySCC25_ECE_competition_tasks.pdf`. 
(The task instructions also include where to find the code)

Use the "Issues" tab in this repo to ask questions, and to browse already-asked questions.

The data for ECE is large, to make access easier we have prepared the data on a manila 
share that you can mount on a jetstream instance:

1. Mount the share with:

   ```
   curl https://jetstream2.exosphere.app/exosphere/assets/scripts/mount_ceph.py | sudo python3 - mount \
      --access-rule-name="indyscc25-input-data-ro" \
      --access-rule-key="AQCzdBFpmAq/NRAAcP197/VoSIsQ5ggwwI/Mgw==" \
      --share-path="149.165.158.38:6789,149.165.158.22:6789,149.165.158.54:6789,149.165.158.70:6789,149.165.158.86:6789:/volumes/_nogroup/9ae266b2-e4a6-49d4-8466-b6837041f1ad/eee8483a-2569-4dbb-bad0-8890ff03bd82" \
      --share-name="indyscc25-input-data"
   ```

2. Untar the data to your own volume, eg:

   ```
   cd /media/volume/my-input-data    # or whatever you called it
   path_to_tar_file="something/sensible/here"
   filename="something_sensible_here"
   tar xzf /media/share/indyscc25-input-data/ECE/${path_to_tar_file}/${filename}.tar.gz 
   ```

3. You can then unmount the share with:

   ```
   curl https://jetstream2.exosphere.app/exosphere/assets/scripts/mount_ceph.py | sudo python3 - unmount \
   --share-name="indyscc25-input-data"
   ```

> [!NOTE]
> Do not run jobs against the input data share: you must first unpack the data to your own volume!

Alternatively, you may [set up a Globus Connect Personal endpoint](https://docs.jetstream-cloud.org/general/filetransfer/)
on your Jetstream instance, and use Globus to pull the data from the
[SC25 Cluster Competitions](https://app.globus.org/file-manager/collections/8351071c-64e1-4d6b-a7dc-65b7d51d8d80)
collection on the [NERSC SHARE](https://app.globus.org/file-manager/collections/b6534bbc-5bb1-11e9-bf33-0edbf3a4e7ee/overview)
Globus endpoint.
