import { useEffect, useMemo, useState } from 'react'
import {
  createAdminRecord,
  deleteAdminRecord,
  listAdminRecords,
  updateAdminRecord,
} from '../api/adminPanel'
import './AdminPanel.css'

const MODEL_CONFIGS = [
  {
    key: 'users',
    label: 'Users',
    endpoint: 'users',
    columns: ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser'],
    fields: [
      field('username', 'Username', 'text', true),
      field('email', 'Email', 'email'),
      field('first_name', 'First name'),
      field('last_name', 'Last name'),
      field('is_active', 'Active', 'checkbox'),
      field('is_staff', 'Staff', 'checkbox'),
      field('is_superuser', 'Superuser', 'checkbox'),
      field('password', 'New password', 'password'),
    ],
  },
  {
    key: 'user-profiles',
    label: 'User Profiles',
    endpoint: 'user-profiles',
    columns: ['id', 'username', 'country', 'university', 'preferred_language'],
    fields: [
      field('user', 'User ID', 'number', true),
      field('country', 'Country'),
      field('university', 'University'),
      field('arrival_date', 'Arrival date', 'date'),
      field('bio', 'Bio', 'textarea'),
      field('preferred_language', 'Language'),
    ],
  },
  {
    key: 'checklist-categories',
    label: 'Checklist Categories',
    endpoint: 'checklist-categories',
    columns: ['id', 'name', 'order', 'icon'],
    fields: [
      field('name', 'Name', 'text', true),
      field('description', 'Description', 'textarea'),
      field('order', 'Order', 'number'),
      field('icon', 'Icon'),
    ],
  },
  {
    key: 'checklist-items',
    label: 'Checklist Items',
    endpoint: 'checklist-items',
    columns: ['id', 'title', 'category_name', 'university', 'is_active'],
    fields: [
      field('category', 'Category ID', 'number', true),
      field('title', 'Title', 'text', true),
      field('slug', 'Slug'),
      field('description', 'Description', 'textarea', true),
      field('detail_description', 'Detail description', 'textarea'),
      field('order', 'Order', 'number'),
      field('resource_url', 'Resource URL', 'url'),
      field('university', 'University'),
      field('estimated_minutes', 'Estimated minutes', 'number'),
      field('is_active', 'Active', 'checkbox'),
    ],
  },
  {
    key: 'checklist-progress',
    label: 'Checklist Progress',
    endpoint: 'checklist-progress',
    columns: ['id', 'username', 'item_title', 'completed', 'completed_at'],
    fields: [
      field('user', 'User ID', 'number', true),
      field('item', 'Item ID', 'number', true),
      field('completed', 'Completed', 'checkbox'),
      field('completed_at', 'Completed at', 'datetime-local'),
    ],
  },
  {
    key: 'service-categories',
    label: 'Service Categories',
    endpoint: 'service-categories',
    columns: ['id', 'name', 'slug', 'order'],
    fields: [
      field('name', 'Name', 'text', true),
      field('slug', 'Slug', 'text', true),
      field('description', 'Description', 'textarea'),
      field('icon', 'Icon'),
      field('order', 'Order', 'number'),
    ],
  },
  {
    key: 'service-entries',
    label: 'Service Entries',
    endpoint: 'service-entries',
    columns: ['id', 'name', 'category_name', 'verified', 'university'],
    fields: [
      field('name', 'Name', 'text', true),
      field('slug', 'Slug'),
      field('category', 'Category ID', 'number'),
      field('description', 'Description', 'textarea', true),
      field('detail_description', 'Detail description', 'textarea'),
      field('address', 'Address', 'text', true),
      field('maps_link', 'Maps link', 'url'),
      field('latitude', 'Latitude', 'number'),
      field('longitude', 'Longitude', 'number'),
      field('phone', 'Phone'),
      field('website', 'Website', 'url'),
      field('tags', 'Tags'),
      field('university', 'University'),
      field('verified', 'Verified', 'checkbox'),
      field('hours', 'Hours'),
    ],
  },
  {
    key: 'posts',
    label: 'Posts',
    endpoint: 'posts',
    columns: ['id', 'title', 'author_username', 'upvotes', 'is_hidden'],
    fields: [
      field('author', 'Author ID', 'number'),
      field('title', 'Title', 'text', true),
      field('body', 'Body', 'textarea', true),
      field('university', 'University'),
      field('upvotes', 'Upvotes', 'number'),
      field('is_hidden', 'Hidden', 'checkbox'),
    ],
  },
  {
    key: 'replies',
    label: 'Replies',
    endpoint: 'replies',
    columns: ['id', 'post_title', 'author_username', 'upvotes', 'is_accepted'],
    fields: [
      field('post', 'Post ID', 'number', true),
      field('author', 'Author ID', 'number'),
      field('body', 'Body', 'textarea', true),
      field('upvotes', 'Upvotes', 'number'),
      field('is_accepted', 'Accepted', 'checkbox'),
    ],
  },
  {
    key: 'bot-faqs',
    label: 'Bot FAQs',
    endpoint: 'bot-faqs',
    columns: ['id', 'trigger_keyword', 'category', 'active'],
    fields: [
      field('trigger_keyword', 'Trigger keyword', 'text', true),
      field('response_text', 'Response text', 'textarea', true),
      field('active', 'Active', 'checkbox'),
      field('category', 'Category'),
    ],
  },
]

function field(name, label, type = 'text', required = false) {
  return { name, label, type, required }
}

function blankRecord(fields) {
  return fields.reduce((acc, f) => {
    acc[f.name] = f.type === 'checkbox' ? false : ''
    return acc
  }, {})
}

function normalizeRecord(record, fields) {
  const next = blankRecord(fields)
  fields.forEach((f) => {
    if (record[f.name] !== undefined && record[f.name] !== null) {
      if (f.type === 'datetime-local') {
        next[f.name] = String(record[f.name]).slice(0, 16)
      } else {
        next[f.name] = record[f.name]
      }
    }
  })
  if (Object.prototype.hasOwnProperty.call(next, 'password')) next.password = ''
  return next
}

function payloadForSave(form, fields) {
  return fields.reduce((acc, f) => {
    const value = form[f.name]
    if (f.name === 'password' && !value) return acc
    if (f.type === 'number') acc[f.name] = value === '' ? null : Number(value)
    else if (f.type === 'checkbox') acc[f.name] = Boolean(value)
    else if (f.type === 'date' || f.type === 'datetime-local') acc[f.name] = value === '' ? null : value
    else acc[f.name] = value
    return acc
  }, {})
}

function renderValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (Array.isArray(value)) return value.join(', ')
  return String(value).length > 80 ? `${String(value).slice(0, 80)}...` : String(value)
}

export default function AdminPanel() {
  const [activeKey, setActiveKey] = useState(MODEL_CONFIGS[0].key)
  const activeModel = useMemo(
    () => MODEL_CONFIGS.find((model) => model.key === activeKey),
    [activeKey]
  )
  const [records, setRecords] = useState([])
  const [selected, setSelected] = useState(null)
  const [mode, setMode] = useState('view')
  const [form, setForm] = useState(blankRecord(activeModel.fields))
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setSelected(null)
    setMode('view')
    setForm(blankRecord(activeModel.fields))
    setSearch('')
  }, [activeModel])

  useEffect(() => {
    const timer = setTimeout(fetchRecords, 250)
    return () => clearTimeout(timer)
  }, [activeModel, search])

  async function fetchRecords() {
    setLoading(true)
    setError('')
    try {
      const { data } = await listAdminRecords(activeModel.endpoint, search)
      setRecords(data.results || data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not load admin records.')
    } finally {
      setLoading(false)
    }
  }

  function startCreate() {
    setSelected(null)
    setMode('create')
    setForm(blankRecord(activeModel.fields))
  }

  function selectRecord(record) {
    setSelected(record)
    setMode('edit')
    setForm(normalizeRecord(record, activeModel.fields))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      const payload = payloadForSave(form, activeModel.fields)
      if (mode === 'create') {
        const { data } = await createAdminRecord(activeModel.endpoint, payload)
        setSelected(data)
        setMode('edit')
        setForm(normalizeRecord(data, activeModel.fields))
      } else if (selected) {
        const { data } = await updateAdminRecord(activeModel.endpoint, selected.id, payload)
        setSelected(data)
        setForm(normalizeRecord(data, activeModel.fields))
      }
      await fetchRecords()
    } catch (err) {
      setError(formatApiError(err.response?.data) || 'Could not save record.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!selected) return
    const confirmed = window.confirm(`Delete ${activeModel.label} #${selected.id}?`)
    if (!confirmed) return
    setSaving(true)
    setError('')
    try {
      await deleteAdminRecord(activeModel.endpoint, selected.id)
      setSelected(null)
      setMode('view')
      setForm(blankRecord(activeModel.fields))
      await fetchRecords()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not delete record.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="admin-page page">
      <div className="page-header">
        <div className="container">
          <h1>Admin Panel</h1>
          <p>Manage application records from one protected workspace.</p>
        </div>
      </div>

      <div className="container admin-layout">
        <aside className="admin-sidebar">
          {MODEL_CONFIGS.map((model) => (
            <button
              key={model.key}
              className={`admin-model-btn ${model.key === activeKey ? 'active' : ''}`}
              onClick={() => setActiveKey(model.key)}
            >
              {model.label}
            </button>
          ))}
        </aside>

        <main className="admin-main">
          <div className="admin-toolbar">
            <input
              type="search"
              placeholder={`Search ${activeModel.label.toLowerCase()}`}
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <button className="btn btn-primary" onClick={startCreate}>Add</button>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <div className="admin-grid">
            <section className="admin-table-wrap card">
              {loading ? (
                <div className="loading-center"><div className="spinner" /></div>
              ) : records.length === 0 ? (
                <div className="empty-state">
                  <h3>No records found</h3>
                  <p>Try another search or add a new record.</p>
                </div>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      {activeModel.columns.map((column) => <th key={column}>{column}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((record) => (
                      <tr
                        key={record.id}
                        className={selected?.id === record.id ? 'active' : ''}
                        onClick={() => selectRecord(record)}
                      >
                        {activeModel.columns.map((column) => (
                          <td key={column}>{renderValue(record[column])}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>

            <section className="admin-editor card">
              <div className="admin-editor__header">
                <h2>{mode === 'create' ? `Add ${activeModel.label}` : selected ? `Edit #${selected.id}` : activeModel.label}</h2>
                {selected && <button className="btn btn-ghost admin-delete" onClick={handleDelete}>Delete</button>}
              </div>

              {mode === 'view' && !selected ? (
                <div className="empty-state">
                  <h3>Select a record</h3>
                  <p>Choose a row to edit or use Add to create one.</p>
                </div>
              ) : (
                <form className="admin-form" onSubmit={handleSubmit}>
                  {activeModel.fields.map((f) => (
                    <AdminField
                      key={f.name}
                      field={f}
                      value={form[f.name]}
                      onChange={(value) => setForm((current) => ({ ...current, [f.name]: value }))}
                    />
                  ))}
                  <button type="submit" className="btn btn-primary" disabled={saving}>
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </form>
              )}
            </section>
          </div>
        </main>
      </div>
    </div>
  )
}

function AdminField({ field, value, onChange }) {
  if (field.type === 'checkbox') {
    return (
      <label className="admin-check">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(event.target.checked)}
        />
        <span>{field.label}</span>
      </label>
    )
  }

  return (
    <div className="form-group">
      <label>
        {field.label}{field.required && <span className="label-hint"> *</span>}
      </label>
      {field.type === 'textarea' ? (
        <textarea
          rows={5}
          value={value || ''}
          required={field.required}
          onChange={(event) => onChange(event.target.value)}
        />
      ) : (
        <input
          type={field.type}
          value={value || ''}
          required={field.required}
          step={field.type === 'number' ? 'any' : undefined}
          onChange={(event) => onChange(event.target.value)}
        />
      )}
    </div>
  )
}

function formatApiError(data) {
  if (!data) return ''
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  return Object.entries(data)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
    .join(' ')
}
