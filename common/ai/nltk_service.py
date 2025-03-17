import nltk
from nltk.corpus import wordnet as wn

#todo blocking code!

# Uncomment if running for the first time to download WordNet data.
# nltk.download('wordnet')

def get_most_similar_entity(target, entity_list):
    # Try to get synsets for the full target.
    target_synsets = wn.synsets(target)

    # If no synsets are found, split target into tokens and collect synsets.
    if not target_synsets:
        tokens = target.split()
        token_synsets = []
        for token in tokens:
            syns = wn.synsets(token)
            if syns:
                token_synsets.extend(syns)
        target_synsets = token_synsets

    if not target_synsets:
        print(f"No synsets found for target '{target}' or its tokens.")
        return None

    best_match = None
    max_similarity = -1  # Start lower than any possible similarity

    for entity in entity_list:
        # If an entity exactly appears in the target tokens, return it immediately.
        if entity.lower() in [tok.lower() for tok in target.split()]:
            return entity

        entity_synsets = wn.synsets(entity)
        if not entity_synsets:
            print(f"No synsets found for entity '{entity}'.")
            continue

        # Compute maximum Wu-Palmer similarity between target and entity synsets.
        current_similarity = 0
        for target_syn in target_synsets:
            for entity_syn in entity_synsets:
                sim = target_syn.wup_similarity(entity_syn)
                if sim is not None and sim > current_similarity:
                    current_similarity = sim

        if current_similarity > max_similarity:
            max_similarity = current_similarity
            best_match = entity

    return best_match


def main():
    # Define the entities list and the target entity.
    entities = ["job"]
    target_entity = "job entity"

    result = get_most_similar_entity(target_entity, entities)
    print("Most semantically similar entity:", result)


if __name__ == '__main__':
    main()
