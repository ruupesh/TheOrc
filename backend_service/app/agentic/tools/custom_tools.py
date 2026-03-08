import json
import csv
import requests


async def check_prime(nums: list[int]) -> str:
    """Check if a given list of numbers are prime.

    Args:
    nums: The list of numbers to check.

    Returns:
    A str indicating which number is prime.
    """
    primes = set()
    for number in nums:
        number = int(number)
        if number <= 1:
            continue
        is_prime = True
        for i in range(2, int(number**0.5) + 1):
            if number % i == 0:
                is_prime = False
            break
        if is_prime:
            primes.add(number)
    return (
        "No prime numbers found."
        if not primes
        else f"{', '.join(str(num) for num in primes)} are prime numbers."
    )


async def check_weather(latitude: float, longitude: float) -> str:
    """Check the weather for a given location. LLM needs to use own knowledge to fetch the latitude and longitude of the provided location to use this tool.

    Args:
    latitude: The latitude of the location.
    longitude: The longitude of the location.
    Returns:
    A str indicating the weather in the location.
    """
    URL = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,visibility,uv_index&past_days=3&forecast_days=3"
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"


async def find_file_path(filename: str) -> str:
    """Find the file path for a given filename.

    Args:
    filename: The name of the file to find.

    Returns:
    A str indicating the file path.
    """
    # Placeholder implementation. Replace with actual file search logic.
    return f"/path/to/{filename}"


def write_to_disk(filename: str, content: str) -> str:
    """Write content to a file on disk. If the content is a JSON string representing a list of dictionaries,
    it will be converted to CSV format before writing. Otherwise, the content is written as is.

    Args:
        filename: The name of the file to write to.
        content: The content to write to the file.

    Returns:
        A string indicating that the file was written successfully.
    """
    try:
        data = json.loads(content)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Assume it's a list of dictionaries, convert to CSV
            output_filename = (
                filename.replace(".json", ".csv")
                if filename.endswith(".json")
                else filename
            )
            with open(output_filename, "w", newline="", encoding="utf-8") as f:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            return f"File '{output_filename}' written successfully in CSV format."
        else:
            # Not a list of dictionaries, write content as is
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{filename}' written successfully."
    except json.JSONDecodeError:
        # Content is not JSON, write as is
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{filename}' written successfully."
        except Exception as e:
            return f"Error writing file '{filename}': {e}"
    except Exception as e:
        return f"Error writing file '{filename}': {e}"


async def get_jobs_listings(company_name: str, role: str) -> str:
    """Generate dummy job data for a given company name and role.

    Args:
        company_name: The name of the company to generate jobs for.
        role: The job role or position to generate listings for.

    Returns:
        A JSON string containing a list of job dictionaries with title, link, and snippet.
    """
    dummy_jobs = [
        {
            "title": f"Senior {role} at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/senior-{role.lower().replace(' ', '-')}",
            "snippet": f"We are hiring a Senior {role} at {company_name}. Lead our team and build scalable solutions.",
        },
        {
            "title": f"{role} at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/{role.lower().replace(' ', '-')}",
            "snippet": f"Join {company_name} as a {role}. Drive innovation in a fast-paced environment.",
        },
        {
            "title": f"Principal {role} at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/principal-{role.lower().replace(' ', '-')}",
            "snippet": f"Exciting opportunity at {company_name} for a Principal {role}. Work on cutting-edge projects.",
        },
        {
            "title": f"Junior {role} at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/junior-{role.lower().replace(' ', '-')}",
            "snippet": f"{company_name} is looking for a Junior {role} to join our growing team.",
        },
        {
            "title": f"{role} (Remote) at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/{role.lower().replace(' ', '-')}-remote",
            "snippet": f"Work remotely as a {role} at {company_name}. Flexible schedule and great benefits.",
        },
        {
            "title": f"{role} - Contract at {company_name}",
            "link": f"https://careers.{company_name.lower().replace(' ', '')}.com/job/{role.lower().replace(' ', '-')}-contract",
            "snippet": f"Contract opportunity for a {role} at {company_name}. 6-month engagement with potential extension.",
        },
    ]
    return json.dumps(dummy_jobs)


async def write_to_disk(filename: str, content: str) -> str:
    """Write content to a file on disk. If the content is a JSON string representing a list of dictionaries,
    it will be converted to CSV format before writing. Otherwise, the content is written as is.

    Args:
        filename: The name of the file to write to.
        content: The content to write to the file.

    Returns:
        A string indicating that the file was written successfully.
    """
    print(f"Writing data : {content} to file: {filename}")
    try:
        data = json.loads(content)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Assume it's a list of dictionaries, convert to CSV
            output_filename = (
                filename.replace(".json", ".csv")
                if filename.endswith(".json")
                else filename
            )
            with open(output_filename, "w", newline="", encoding="utf-8") as f:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            return f"File '{output_filename}' written successfully in CSV format."
        else:
            # Not a list of dictionaries, write content as is
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{filename}' written successfully."
    except json.JSONDecodeError:
        # Content is not JSON, write as is
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{filename}' written successfully."
        except Exception as e:
            return f"Error writing file '{filename}': {e}"
    except Exception as e:
        return f"Error writing file '{filename}': {e}"
