/**
 * Profile page (/profile, logged-in users only): name and headline, the three lists
 * (education, experience, projects), and changing the password.
 *
 * It loads the whole profile once (`GET /profile`) and holds it; each section saves its
 * own changes and hands back its new list.
 */
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { type ErrorKey, errorKey } from "../api/errors";
import { type Entry, type EntryKind, getProfile, type Profile } from "../api/profile";
import { ChangePasswordForm } from "../components/ChangePasswordForm";
import { EntrySection } from "../components/EntrySection";
import { ProfileDetailsForm } from "../components/ProfileDetailsForm";
import { ENTRY_KINDS } from "../profile/entryKinds";

export function ProfilePage() {
  const { t } = useTranslation();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [failure, setFailure] = useState<ErrorKey | null>(null);

  useEffect(() => {
    let active = true;
    getProfile()
      .then((loaded) => active && setProfile(loaded))
      .catch((error: unknown) => active && setFailure(errorKey(error)));
    return () => {
      active = false;
    };
  }, []);

  if (failure) {
    return (
      <main>
        <h1>{t("profile.title")}</h1>
        <p className="form-error" role="alert">
          {t(failure)}
        </p>
      </main>
    );
  }
  if (!profile) {
    return (
      <main>
        <h1>{t("profile.title")}</h1>
        <p role="status">{t("profile.loading")}</p>
      </main>
    );
  }

  const setList = (kind: EntryKind) => (entries: Entry[]) =>
    setProfile((old) => (old ? { ...old, [kind]: entries } : old));

  return (
    <main className="profile-page">
      <h1>{t("profile.title")}</h1>
      <ProfileDetailsForm profile={profile} onSaved={setProfile} />
      {ENTRY_KINDS.map((spec) => (
        <EntrySection
          key={spec.kind}
          spec={spec}
          entries={profile[spec.kind]}
          onChange={setList(spec.kind)}
        />
      ))}
      <section className="entry-section" aria-labelledby="section-password">
        <h2 id="section-password">{t("password.title")}</h2>
        <ChangePasswordForm />
      </section>
    </main>
  );
}
