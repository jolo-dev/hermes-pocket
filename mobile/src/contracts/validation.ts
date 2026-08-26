import Ajv2020, { type ValidateFunction } from 'ajv/dist/2020';
import addFormats from 'ajv-formats';
import { mobileApiSchema, type components } from '../generated/api';

type SchemaName = keyof components['schemas'];
const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
ajv.addSchema(mobileApiSchema);

export function parseApiModel<Name extends SchemaName>(
  name: Name,
  value: unknown,
): components['schemas'][Name] {
  const id = `${mobileApiSchema.$id}#/$defs/${name}`;
  const validate = ajv.getSchema(id) as ValidateFunction<components['schemas'][Name]> | undefined;
  if (!validate || !validate(value)) {
    throw new Error(`Invalid ${name}`);
  }
  return value;
}
