'use client';

interface Props {
  collections: string[];
  active: string;
  onSelect: (col: string) => void;
}

export default function CollectionSelector({ collections, active, onSelect }: Props) {
  return (
    <select
      value={active}
      onChange={e => onSelect(e.target.value)}
      className="bg-gray-800 border border-gray-700 rounded-lg p-2 text-gray-100"
    >
      {collections.length === 0 ? (
        <option value="">No collections</option>
      ) : (
        <>
          <option value="">Select Collection</option>
          {collections.map((c, i) => (
            <option key={i} value={c}>
              {c}
            </option>
          ))}
        </>
      )}
    </select>
  );
}
