import { describe, expect, it } from 'vitest'

import { ApiError } from './client'
import { apiErrorMessage, withQuery } from './errors'

describe('apiErrorMessage', () => {
  it('prefers the server conflict message', () => {
    const error = new ApiError(409, {
      error: {
        message: 'Delivery already exists for this hostel and date',
        details: [{ field: 'delivery_date', message: 'already exists' }],
      },
    })
    expect(apiErrorMessage(error, 'Could not save delivery')).toBe(
      'Delivery already exists for this hostel and date',
    )
  })

  it('falls back when the body has no message', () => {
    expect(apiErrorMessage(new Error('nope'), 'Could not save')).toBe('Could not save')
  })
})

describe('withQuery', () => {
  it('omits empty filters', () => {
    expect(withQuery('/api/v1/deliveries', { page: '1', hostel_id: undefined })).toBe(
      '/api/v1/deliveries?page=1',
    )
  })
})
