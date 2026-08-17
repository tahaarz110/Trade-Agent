"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchFieldDefinitions, fetchFieldSections } from "@/lib/api";
import type { SectionWithFields } from "@/lib/types";

export function useDynamicFieldSchema() {
  const sectionsQuery = useQuery({
    queryKey: ["field-sections"],
    queryFn: () => fetchFieldSections(false),
  });
  const fieldsQuery = useQuery({
    queryKey: ["field-definitions"],
    queryFn: () => fetchFieldDefinitions(false),
  });

  const sections: SectionWithFields[] = (sectionsQuery.data ?? [])
    .slice()
    .sort((a, b) => a.sort_order - b.sort_order)
    .map((section) => ({
      ...section,
      fields: (fieldsQuery.data ?? [])
        .filter((f) => f.section_id === section.id && f.show_in_form)
        .sort((a, b) => a.sort_order - b.sort_order),
    }))
    .filter((section) => section.fields.length > 0);

  return {
    sections,
    isLoading: sectionsQuery.isLoading || fieldsQuery.isLoading,
    isError: sectionsQuery.isError || fieldsQuery.isError,
  };
}
