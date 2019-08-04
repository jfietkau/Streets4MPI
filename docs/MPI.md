##Streets4MPI class behavior

Begins by reading in MPI information

Sets up the simulation constraints (Every rank)

- Sets random seed
- Reads and builds OSM street data to graph
- Builds a street network
- Checks node categories the read in OSM data
- Generates trips to simulate?
- Take chunk of work based on num_ranks (a.k.a. threads available to MPI)
- Processes it

On rank 0

- Reads in persist_traffic_load variable







(core/thread independent)





