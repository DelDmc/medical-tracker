/** The designated informational page (ADS-PRV-003-01, user_flows.md §23). */
export function AboutPage() {
  return (
    <section className="page" aria-labelledby="about-title">
      <h1 id="about-title">About Medical Tracker</h1>

      <div className="card" id="purpose-statement">
        <p>
          <strong>
            Medical Tracker is an organizational tool. It does not provide medical advice,
            diagnosis, treatment, or emergency assistance.
          </strong>
        </p>
        <p>
          It helps you keep your own medical appointments and examination history in one place:
          completed examinations, drafts, planned examinations, in-application reminders, and
          recurring checkups.
        </p>
      </div>

      <div className="card">
        <h2>What it does not do</h2>
        <ul>
          <li>It does not provide medical advice.</li>
          <li>It does not provide a diagnosis.</li>
          <li>It does not provide treatment or treatment recommendations.</li>
          <li>It does not provide emergency assistance.</li>
        </ul>
        <p>The application never interprets your notes or makes recommendations about your health.</p>
      </div>

      <div className="card">
        <h2>What it stores</h2>
        <p>
          Only appointment and examination details: a title, an optional category and medical
          specialty, scheduled and completion dates, an optional time, a location, and general
          notes, plus your email address and timezone for your account.
        </p>
        <p>
          It does not ask for diagnoses, prescriptions, medical files, insurance information, or
          government identification numbers, and you do not need to enter any of them.
        </p>
      </div>
    </section>
  )
}
