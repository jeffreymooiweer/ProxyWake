import i18n from '../i18n';

export const translateApiPayload = (data) => {
  if (!data) return data;

  if (data.error_code) {
    const key = `errors.${data.error_code}`;
    const translated = i18n.t(key, data);
    throw new Error(translated === key ? data.error : translated);
  }

  if (data.message_code) {
    return {
      ...data,
      message: i18n.t(`messages.${data.message_code}`, data),
    };
  }

  return data;
};
