import fixture from '../../contracts/fixtures/v1/api-models.json';
import { parseApiModel } from '../src/contracts/validation';

test('shared fixtures parse through generated API models', () => {
  expect(parseApiModel('DeviceSession', fixture.session).device_session_id).toBe('device-fixture-1');
  expect(parseApiModel('EventEnvelope', fixture.event).sequence).toBe(1);
  expect(parseApiModel('Approval', fixture.approval).status).toBe('pending');
  expect(parseApiModel('Task', fixture.task).kind).toBe('reminder');
  expect(parseApiModel('PrivacyRecord', fixture.privacy_record).category).toBe('share');
});

test('runtime parsing rejects undeclared fields and invalid bounds', () => {
  expect(() => parseApiModel('EventEnvelope', { ...fixture.event, raw_screen: 'never allowed' })).toThrow('Invalid EventEnvelope');
  expect(() => parseApiModel('SharedContextPart', { ...fixture.shared_context.parts[0], size_bytes: 10485761 })).toThrow('Invalid SharedContextPart');
});
