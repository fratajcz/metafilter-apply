import argparse
from metapathWalking import getConfiguredLogger

parser = argparse.ArgumentParser(description='Walk a Graph along Metapaths and store complete walks.')

parser.add_argument('--input', "-i", type=str,
                    help='path to the full walks file')
parser.add_argument('--output', "-o", type=str,
                    help='path to the uniquefied node ids')


args = parser.parse_args()


logger = getConfiguredLogger("Process Walks")

def buf_count_newlines_gen(fname):
    def _make_gen(reader):
        while True:
            b = reader(2 ** 16)
            if not b: break
            yield b

    with open(fname, "rb") as f:
        count = sum(buf.count(b"\n") for buf in _make_gen(f.raw.read))
    return count

logger.info("Counting complete walks...")

line_count = buf_count_newlines_gen(args.input)
ten_percent = int(line_count/10)


logger.info("{} Walks waiting to be processed.".format(line_count))

unique_ids = set()
with open(args.input,"r") as input:
    counter = 0
    percentage = 1
    for i, line in enumerate(input):
        unique_ids.update(line.split(" "))
        counter += 1
        if counter == ten_percent:
            logger.info("Processed {}0% of walks".format(percentage))
            percentage += 1
            counter = 0

with open(args.output,"w") as output:
    for id in unique_ids:
        if id != "":
            output.write(str(id) + "\n")


logger.info("Identified {} unique ids.".format(buf_count_newlines_gen(args.output)))