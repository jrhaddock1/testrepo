#!/usr/bin/python
import sys
import argparse
import subprocess

__author__ = "Josh Haddock"
__email__ = "jrhaddock1@gmail.com"

def main():
    """Parses args, then ..."""
    args = parse_args()

    try:
        bwa_ref = "/home/jrhaddock1/tiny-test-data/genomes/Hsapiens/hg19/bwa/hg19.fa"
        sam_ref = "/home/jrhaddock1/tiny-test-data/genomes/Hsapiens/hg19/seq/hg19.fa"
        input_sample_name = args.input_sample_name

        # Run BWA-MEM
        bwa_alignment_command = f"bwa mem {bwa_ref} {input_sample_name}_1.fq.gz {input_sample_name}_2.fq.gz > {input_sample_name}.sam"
        subprocess.call(bwa_alignment_command, shell=True)

        # Sort the SAM file with Samtools
        samtools_sort_command = f"samtools sort {input_sample_name}.sam -o {input_sample_name}_s.bam"
        subprocess.call(samtools_sort_command, shell=True)

        # Run Samtools mpileup and BCFtools call
        samtools_mpileup_command = f"samtools mpileup -Ou -f {sam_ref} {input_sample_name}_s.bam | bcftools call -vmO v -o {input_sample_name}.vcf"
        subprocess.call(samtools_mpileup_command, shell=True)

        # Calculate the average QUAL score
        average_qual = calculate_average_qual(f"{input_sample_name}.vcf")
        print(f"Average QUAL score: {average_qual:.2f}")

    except Exception as err:
        print(f"An error occurred: {err}")

def calculate_average_qual(vcf_file):
    total_qual = 0
    total_count = 0

    with open(vcf_file, 'r') as vcf_reader:
        for line in vcf_reader:
            if not line.startswith("#"):
                parts = line.strip().split("\t")
                qual = float(parts[5])
                total_qual += qual
                total_count += 1

    if total_count > 0:
        average_qual = total_qual / total_count
        return average_qual
    else:
        return 0  # Return 0 if no records with QUAL values are found        

def parse_args():
    """Standard argument parsing"""
    parser = argparse.ArgumentParser(description="My Variant Calling Pipeline Script")

    parser.add_argument('-i', '--input_sample_name', type=str, required=True, help='Base sample name')

    return parser.parse_args()

if __name__ == "__main__":
    sys.exit(main())
