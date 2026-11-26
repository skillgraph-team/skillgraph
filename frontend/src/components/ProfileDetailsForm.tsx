/** The name and headline at the top of the profile (`PATCH /profile`). */
import { type FormEvent, useId, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { type Profile, updateProfile } from "../api/profile";
import { MAX_LENGTH } from "../profile/entryKinds";

interface Props {
  profile: Profile;
  onSaved(profile: Profile): void;
}

export function ProfileDetailsForm({ profile, onSaved }: Props) {
  const { t } = useTranslation();
  const id = useId();
  const [name, setName] = useState(profile.display_name ?? "");
  const [headline, setHeadline] = useState(profile.headline ?? "");
  const [result, setResult] = useState<ErrorKey | "saved" | null>(null);
  const [sending, setSending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSending(true);
    setResult(null);
    try {
      onSaved(
        await updateProfile({
          display_name: name.trim() || null,
          headline: headline.trim() || null,
        }),
      );
      setResult("saved");
    } catch (error) {
      setResult(errorKey(error));
    }
    setSending(false);
  }

  return (
    <form className="entry-form" noValidate onSubmit={(event) => void submit(event)}>
      <div className="field">
        <label htmlFor={`${id}-name`}>{t("profile.fields.display_name")}</label>
        <input
          id={`${id}-name`}
          dir="auto"
          maxLength={MAX_LENGTH.short}
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor={`${id}-headline`}>{t("profile.fields.headline")}</label>
        <input
          id={`${id}-headline`}
          dir="auto"
          maxLength={MAX_LENGTH.short}
          value={headline}
          onChange={(event) => setHeadline(event.target.value)}
        />
      </div>
      {result === "saved" && <p role="status">{t("profile.saved")}</p>}
      {result && result !== "saved" && (
        <p className="form-error" role="alert">
          {t(result)}
        </p>
      )}
      <div className="buttons">
        <button type="submit" disabled={sending}>
          {t("profile.save")}
        </button>
      </div>
    </form>
  );
}
