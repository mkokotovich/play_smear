function getErrorString(data) {
  console.log(`In getErrorString: ${data}`)
  if (data.status && data.status === "error" && data.error) {
    console.log(`Well formed error`)
    // This is a well-formed error from our API
    if (data.error.error === "Validation Error") {
      console.log(`Validation Error`)
      // Just the first Validation Error, for simplicity
      return data.error.validation_errors.meta[0];
    } else {
      return data.error.error_description;
    }
  } else {
    return JSON.stringify(data)
  }
}

export default getErrorString;
