import mailbox
import argparse
import os

def split_mbox(source_file, output_prefix, max_messages=None, max_size_mb=None):
    """
    Splits a large MBOX file into smaller parts based on message count or file size.

    Args:
        source_file (str): Path to the source MBOX file.
        output_prefix (str): Prefix for the output files (e.g., "split_archive").
        max_messages (int, optional): Maximum number of messages per output file.
        max_size_mb (int, optional): Maximum size in megabytes per output file.
    """
    print(f"Opening source file: {source_file}")
    try:
        source_mbox = mailbox.mbox(source_file)
    except FileNotFoundError:
        print(f"Error: Source file not found at '{source_file}'")
        return

    part_num = 1
    msg_count = 0
    current_size_bytes = 0
    output_mbox = None

    # Determine the split criteria
    if max_messages:
        split_by = 'messages'
        limit = max_messages
        print(f"Splitting every {limit} messages.")
    elif max_size_mb:
        split_by = 'size'
        limit = max_size_mb * 1024 * 1024
        print(f"Splitting every {max_size_mb} MB.")
    else:
        # Default to splitting by messages if no criteria is provided
        split_by = 'messages'
        limit = 1000
        print(f"No split criteria provided. Defaulting to split every {limit} messages.")


    for i, message in enumerate(source_mbox):
        # Check if we need to create a new output file
        new_file_needed = False
        if output_mbox is None:
            new_file_needed = True
        elif split_by == 'messages' and msg_count >= limit:
            new_file_needed = True
        elif split_by == 'size' and current_size_bytes >= limit:
            new_file_needed = True

        if new_file_needed:
            if output_mbox:
                output_mbox.close()
                print(f"Closed '{output_filename}'. Contains {msg_count} messages.")

            # Start a new file
            output_filename = f"{output_prefix}_{part_num}.mbox"
            print(f"Creating new split file: '{output_filename}'")
            output_mbox = mailbox.mbox(output_filename)
            part_num += 1
            msg_count = 0
            current_size_bytes = 0

        # Add the current message to the output file
        output_mbox.add(message)
        msg_count += 1
        # Getting the message as a bytes string is a reliable way to check its size
        current_size_bytes += len(message.as_bytes())

        # Provide progress update
        if (i + 1) % 5000 == 0:
            print(f"Processed {i + 1} messages...")

    # Close the last file
    if output_mbox:
        output_mbox.close()
        print(f"Closed final file '{output_filename}'. Contains {msg_count} messages.")

    print("\nSplitting complete! ✅")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split a large MBOX file into smaller parts.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("source_file", help="Path to the large source MBOX file.")
    parser.add_argument(
        "-m", "--max-messages", type=int,
        help="Maximum number of messages per split file (e.g., 1000)."
    )
    parser.add_argument(
        "-s", "--max-size", type=int,
        help="Maximum size in MB per split file (e.g., 500)."
    )

    args = parser.parse_args()

    if not args.max_messages and not args.max_size:
        print("Error: You must specify a split criteria: either --max-messages or --max-size.")
        parser.print_help()
    else:
        # Create an output prefix based on the source filename
        prefix = os.path.splitext(os.path.basename(args.source_file))[0]
        split_mbox(args.source_file, prefix, args.max_messages, args.max_size)
