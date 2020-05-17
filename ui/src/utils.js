function getErrorString(data) {
  console.log("In getErrorString:", data)
  if (data.status && data.status === "error" && data.error) {
    console.log(`Well formed error`)
    // This is a well-formed error from our API
    if (data.error.error === "Validation Error") {
      console.log(`Validation Error`)
      const validation_error = data.error.validation_errors.meta;
      if (Array.isArray(validation_error)) {
        // Just the first Validation Error, for simplicity
        return validation_error[0];
      } else {
        // Return first error from the first field
        const [field, error_list] = Object.entries(validation_error)[0];
        return `Invalid ${field}. ${error_list[0]}`;
      }
    } else {
      return data.error.error_description;
    }
  } else {
    return JSON.stringify(data)
  }
}

export default getErrorString;
